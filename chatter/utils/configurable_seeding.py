"""Enhanced database seeding with YAML configuration support."""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

from chatter.utils.seeding import DatabaseSeeder as BaseDatabaseSeeder, SeedingMode
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigurableSeeder(BaseDatabaseSeeder):
    """Enhanced seeder that loads configuration from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None, session=None):
        """Initialize seeder with optional configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            session: Database session
        """
        super().__init__(session)
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self) -> str:
        """Find the seed data configuration file."""
        # Look in project root, docs directory, and current directory
        possible_paths = [
            Path(__file__).parent.parent / "seed_data.yaml",
            Path(__file__).parent.parent / "docs" / "seed_data.yaml",
            Path("seed_data.yaml"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        logger.warning("No seed data configuration file found")
        return ""
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path or not Path(self.config_path).exists():
            logger.info("Using default seed data configuration")
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded seed configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}
    
    async def _create_development_users(self, skip_existing: bool = True) -> List:
        """Create development users from configuration."""
        if not self.config.get("development_users"):
            logger.info("No development users in configuration, using defaults")
            return await super()._create_development_users(skip_existing)
        
        users_data = self.config["development_users"]
        created_users = []
        
        for user_data in users_data:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.user import User
                existing = await self.session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                if existing.scalar_one_or_none():
                    logger.info(f"User {user_data['username']} already exists, skipping")
                    continue
            
            from chatter.models.user import User
            from chatter.utils.security_enhanced import hash_password
            
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_verified=True,
                is_superuser=user_data.get("is_superuser", False),
                bio=user_data.get("bio", f"Development user: {user_data['full_name']}"),
            )
            
            self.session.add(user)
            created_users.append(user)
        
        if created_users:
            await self.session.commit()
            for user in created_users:
                await self.session.refresh(user)
        
        logger.info(f"Created {len(created_users)} development users from configuration")
        return created_users
    
    async def _create_basic_profiles(self, admin_user, skip_existing: bool = True) -> int:
        """Create profiles from configuration."""
        if not admin_user:
            from sqlalchemy import select
            from chatter.models.user import User
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping profile creation")
                return 0
        
        profiles_config = self.config.get("chat_profiles", {}).get("basic", [])
        if not profiles_config:
            logger.info("No basic profiles in configuration, using defaults")
            return await super()._create_basic_profiles(admin_user, skip_existing)
        
        created_count = 0
        for profile_data in profiles_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.profile import Profile
                existing = await self.session.execute(
                    select(Profile).where(Profile.name == profile_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.profile import Profile, ProfileType
            
            profile = Profile(
                owner_id=admin_user.id,
                name=profile_data["name"],
                description=profile_data["description"],
                profile_type=ProfileType[profile_data["profile_type"]],
                llm_provider=profile_data["llm_provider"],
                llm_model=profile_data["llm_model"],
                temperature=profile_data["temperature"],
                max_tokens=profile_data["max_tokens"],
                top_p=profile_data.get("top_p"),
                system_prompt=profile_data.get("system_prompt"),
                is_public=True,
            )
            
            self.session.add(profile)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} basic profiles from configuration")
        return created_count
    
    async def _create_demo_profiles(self, skip_existing: bool = True) -> List:
        """Create extended profiles for demo mode."""
        profiles_config = self.config.get("chat_profiles", {}).get("extended", [])
        if not profiles_config:
            return []
        
        # Get admin user
        from sqlalchemy import select
        from chatter.models.user import User
        result = await self.session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            logger.warning("No admin user found for demo profiles")
            return []
        
        created_profiles = []
        for profile_data in profiles_config:
            if skip_existing:
                from chatter.models.profile import Profile
                existing = await self.session.execute(
                    select(Profile).where(Profile.name == profile_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.profile import Profile, ProfileType
            
            profile = Profile(
                owner_id=admin_user.id,
                name=profile_data["name"],
                description=profile_data["description"],
                profile_type=ProfileType[profile_data["profile_type"]],
                llm_provider=profile_data["llm_provider"],
                llm_model=profile_data["llm_model"],
                temperature=profile_data["temperature"],
                max_tokens=profile_data["max_tokens"],
                system_prompt=profile_data.get("system_prompt"),
                is_public=True,
            )
            
            self.session.add(profile)
            created_profiles.append(profile)
        
        if created_profiles:
            await self.session.commit()
            for profile in created_profiles:
                await self.session.refresh(profile)
        
        logger.info(f"Created {len(created_profiles)} demo profiles from configuration")
        return created_profiles
    
    async def _create_basic_prompts(self, admin_user, skip_existing: bool = True) -> int:
        """Create prompts from configuration."""
        if not admin_user:
            from sqlalchemy import select
            from chatter.models.user import User
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping prompt creation")
                return 0
        
        prompts_config = self.config.get("prompt_templates", {}).get("basic", [])
        if not prompts_config:
            logger.info("No basic prompts in configuration, using defaults")
            return await super()._create_basic_prompts(admin_user, skip_existing)
        
        created_count = 0
        for prompt_data in prompts_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.prompt import Prompt
                existing = await self.session.execute(
                    select(Prompt).where(Prompt.name == prompt_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.prompt import Prompt, PromptCategory, PromptType
            
            prompt = Prompt(
                owner_id=admin_user.id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                prompt_type=PromptType.TEMPLATE,
                category=PromptCategory[prompt_data["category"]],
                content=prompt_data["content"],
                variables=prompt_data["variables"],
                suggested_temperature=prompt_data.get("suggested_temperature"),
                suggested_max_tokens=prompt_data.get("suggested_max_tokens"),
                is_public=True,
            )
            
            self.session.add(prompt)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} basic prompts from configuration")
        return created_count
    
    async def _create_production_prompts(self, admin_user, skip_existing: bool = True) -> int:
        """Create production prompts from configuration."""
        if not admin_user:
            from sqlalchemy import select
            from chatter.models.user import User
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping production prompt creation")
                return 0
        
        prompts_config = self.config.get("production_data", {}).get("prompt_templates", [])
        if not prompts_config:
            logger.info("No production prompts in configuration, falling back to basic prompts")
            return await self._create_basic_prompts(admin_user, skip_existing)
        
        created_count = 0
        for prompt_data in prompts_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.prompt import Prompt
                existing = await self.session.execute(
                    select(Prompt).where(Prompt.name == prompt_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.prompt import Prompt, PromptCategory, PromptType
            
            prompt = Prompt(
                owner_id=admin_user.id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                prompt_type=PromptType.TEMPLATE,
                category=PromptCategory[prompt_data["category"]],
                content=prompt_data["content"],
                variables=prompt_data["variables"],
                examples=prompt_data.get("examples"),
                suggested_temperature=prompt_data.get("suggested_temperature"),
                suggested_max_tokens=prompt_data.get("suggested_max_tokens"),
                is_public=True,
            )
            
            self.session.add(prompt)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} production prompts from configuration")
        return created_count

    async def _create_production_profiles(self, admin_user, skip_existing: bool = True) -> int:
        """Create production profiles from configuration."""
        if not admin_user:
            from sqlalchemy import select
            from chatter.models.user import User
            result = await self.session.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.warning("No admin user found, skipping production profile creation")
                return 0
        
        profiles_config = self.config.get("production_data", {}).get("chat_profiles", [])
        if not profiles_config:
            logger.info("No production profiles in configuration, falling back to basic profiles")
            return await self._create_basic_profiles(admin_user, skip_existing)
        
        created_count = 0
        for profile_data in profiles_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.profile import Profile
                existing = await self.session.execute(
                    select(Profile).where(Profile.name == profile_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.profile import Profile, ProfileType
            
            profile = Profile(
                owner_id=admin_user.id,
                name=profile_data["name"],
                description=profile_data["description"],
                profile_type=ProfileType[profile_data["profile_type"]],
                llm_provider=profile_data["llm_provider"],
                llm_model=profile_data["llm_model"],
                temperature=profile_data["temperature"],
                max_tokens=profile_data["max_tokens"],
                top_p=profile_data.get("top_p"),
                top_k=profile_data.get("top_k"),
                system_prompt=profile_data.get("system_prompt"),
                enable_tools=profile_data.get("enable_tools", False),
                is_public=True,
                tags=profile_data.get("tags", []),
            )
            
            self.session.add(profile)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {created_count} production profiles from configuration")
        return created_count
    
    async def _seed_production_data(self, results: Dict[str, Any], skip_existing: bool):
        """Override production seeding to use configuration data."""
        logger.info("Seeding production data from configuration")
        
        # Create admin user
        admin_user = await self._create_admin_user(skip_existing)
        if admin_user:
            results["created"]["admin_user"] = admin_user.username
        
        # Create production profiles and prompts from configuration
        profiles_created = await self._create_production_profiles(admin_user, skip_existing)
        prompts_created = await self._create_production_prompts(admin_user, skip_existing)
        
        results["created"]["profiles"] = profiles_created
        results["created"]["prompts"] = prompts_created
        
        # Create default registry data (providers, models, embedding spaces)
        await self._create_default_registry_data(skip_existing)
        results["created"]["registry"] = "default_models"
        
        logger.info(f"Production seeding completed: {profiles_created} profiles, {prompts_created} prompts")
    
    async def _create_demo_prompts(self, skip_existing: bool = True) -> List:
        """Create extended prompts for demo mode."""
        prompts_config = self.config.get("prompt_templates", {}).get("extended", [])
        if not prompts_config:
            return []
        
        # Get admin user
        from sqlalchemy import select
        from chatter.models.user import User
        result = await self.session.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            logger.warning("No admin user found for demo prompts")
            return []
        
        created_prompts = []
        for prompt_data in prompts_config:
            if skip_existing:
                from chatter.models.prompt import Prompt
                existing = await self.session.execute(
                    select(Prompt).where(Prompt.name == prompt_data["name"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.prompt import Prompt, PromptCategory, PromptType
            
            prompt = Prompt(
                owner_id=admin_user.id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                prompt_type=PromptType.TEMPLATE,
                category=PromptCategory[prompt_data["category"]],
                content=prompt_data["content"],
                variables=prompt_data["variables"],
                suggested_temperature=prompt_data.get("suggested_temperature"),
                suggested_max_tokens=prompt_data.get("suggested_max_tokens"),
                is_public=True,
            )
            
            self.session.add(prompt)
            created_prompts.append(prompt)
        
        if created_prompts:
            await self.session.commit()
            for prompt in created_prompts:
                await self.session.refresh(prompt)
        
        logger.info(f"Created {len(created_prompts)} demo prompts from configuration")
        return created_prompts
    
    async def _create_sample_conversations(self, users: List, skip_existing: bool = True) -> int:
        """Create sample conversations from configuration."""
        conversations_config = self.config.get("sample_conversations", [])
        if not conversations_config or not users:
            logger.info("No sample conversations in configuration or no users")
            return await super()._create_sample_conversations(users, skip_existing)
        
        created_count = 0
        for conv_data in conversations_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.conversation import Conversation
                existing = await self.session.execute(
                    select(Conversation).where(Conversation.title == conv_data["title"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.conversation import Conversation, ConversationStatus, Message, MessageRole
            
            # Use first user for conversations
            user = users[0]
            
            conversation = Conversation(
                user_id=user.id,
                title=conv_data["title"],
                description=conv_data.get("description", ""),
                status=ConversationStatus.ACTIVE,
            )
            
            self.session.add(conversation)
            await self.session.commit()
            await self.session.refresh(conversation)
            
            # Add messages
            for msg_data in conv_data.get("messages", []):
                message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole[msg_data["role"]],
                    content=msg_data["content"],
                )
                self.session.add(message)
            
            await self.session.commit()
            created_count += 1
        
        logger.info(f"Created {created_count} sample conversations from configuration")
        return created_count
    
    async def _create_sample_documents(self, users: List, skip_existing: bool = True) -> int:
        """Create sample documents from configuration."""
        documents_config = self.config.get("sample_documents", [])
        if not documents_config or not users:
            logger.info("No sample documents in configuration or no users")
            return await super()._create_sample_documents(users, skip_existing)
        
        created_count = 0
        for doc_data in documents_config:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.document import Document
                existing = await self.session.execute(
                    select(Document).where(Document.filename == doc_data["filename"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
            
            user = users[0]
            
            document = Document(
                user_id=user.id,
                filename=doc_data["filename"],
                title=doc_data["title"],
                content=doc_data["content"],
                document_type=DocumentType[doc_data["doc_type"]],
                file_size=len(doc_data["content"]),
                status=DocumentStatus.PROCESSED,
                chunk_count=1,
            )
            
            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)
            
            # Create document chunk
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=0,
                content=doc_data["content"],
                token_count=len(doc_data["content"].split()),
                metadata={"title": doc_data["title"]},
            )
            
            self.session.add(chunk)
            created_count += 1
        
        if created_count > 0:
            await self.session.commit()
        
        logger.info(f"Created {len(created_count)} sample documents from configuration")
        return created_count
    
    async def _create_test_users(self, skip_existing: bool = True) -> List:
        """Create test users from configuration."""
        test_config = self.config.get("test_data", {})
        users_data = test_config.get("users", [])
        
        if not users_data:
            logger.info("No test users in configuration, using defaults")
            return await super()._create_test_users(skip_existing)
        
        created_users = []
        for user_data in users_data:
            if skip_existing:
                from sqlalchemy import select
                from chatter.models.user import User
                existing = await self.session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                if existing.scalar_one_or_none():
                    continue
            
            from chatter.models.user import User
            from chatter.utils.security_enhanced import hash_password
            
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_verified=True,
                is_superuser=False,
                bio="Test user for automated testing",
            )
            
            self.session.add(user)
            created_users.append(user)
        
        if created_users:
            await self.session.commit()
            for user in created_users:
                await self.session.refresh(user)
        
        logger.info(f"Created {len(created_users)} test users from configuration")
        return created_users


# Enhanced convenience function
async def seed_database_with_config(
    mode: SeedingMode = SeedingMode.DEVELOPMENT,
    config_path: Optional[str] = None,
    force: bool = False,
    skip_existing: bool = True
) -> Dict[str, Any]:
    """Seed database using configuration file."""
    async with ConfigurableSeeder(config_path) as seeder:
        return await seeder.seed_database(mode, force, skip_existing)