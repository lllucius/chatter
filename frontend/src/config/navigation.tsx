import React from 'react';
import {
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  Description as DocumentIcon,
  AccountBox as ProfileIcon,
  TextSnippet as PromptIcon,
  SmartToy as AgentIcon,
  BarChart as AnalyticsIcon,
  HealthAndSafety as HealthIcon,
  AdminPanelSettings as AdminIcon,
  Storage as ModelsIcon,
  Build as ToolsIcon,
  AccountTree as WorkflowIcon,
  Science as ABTestIcon,
} from '@mui/icons-material';

export interface NavItem {
  label: string;
  path: string;
  icon: React.ReactElement;
}

export interface NavSection {
  title: string;
  items: NavItem[];
  defaultExpanded?: boolean;
}

export const navSections: NavSection[] = [
  {
    title: 'Core',
    defaultExpanded: true,
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Chat', path: '/chat', icon: <ChatIcon /> },
    ]
  },
  {
    title: 'Content Management', 
    defaultExpanded: true,
    items: [
      { label: 'Conversations', path: '/conversations', icon: <AnalyticsIcon /> },
      { label: 'Documents', path: '/documents', icon: <DocumentIcon /> },
      { label: 'Profiles', path: '/profiles', icon: <ProfileIcon /> },
      { label: 'Prompts', path: '/prompts', icon: <PromptIcon /> },
    ]
  },
  {
    title: 'AI & Models',
    defaultExpanded: true,
    items: [
      { label: 'Models', path: '/models', icon: <ModelsIcon /> },
      { label: 'Agents', path: '/agents', icon: <AgentIcon /> },
      { label: 'Tools', path: '/tools', icon: <ToolsIcon /> },
      { label: 'Workflows', path: '/workflows', icon: <WorkflowIcon /> },
      { label: 'A/B Testing', path: '/ab-testing', icon: <ABTestIcon /> },
    ]
  },
  {
    title: 'System',
    defaultExpanded: false,
    items: [
      { label: 'Administration', path: '/administration', icon: <AdminIcon /> },
      { label: 'Health', path: '/health', icon: <HealthIcon /> },
    ]
  }
];