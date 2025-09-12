import React, { useRef } from 'react';
import { CrudPageHeader } from '../components/PageHeader';
import { Typography } from '../utils/mui';
import { RefreshIcon, AddIcon } from '../utils/icons';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn, CrudDataTableRef } from '../components/CrudDataTable';
import ProfileForm from '../components/ProfileForm';
import { 
  createNameWithDescriptionRenderer, 
  createCategoryChipRenderer,
  createMonospaceTextRenderer 
} from '../components/CrudRenderers';
import { getSDK } from "../services/auth-service";
import { ProfileResponse, ProfileCreate, ProfileUpdate } from 'chatter-sdk';

const ProfilesPage: React.FC = () => {
  const crudTableRef = useRef<CrudDataTableRef>(null);
  // Define columns
  const columns: CrudColumn<ProfileResponse>[] = [
    {
      id: 'name',
      label: 'Name',
      width: '200px',
      render: createNameWithDescriptionRenderer<ProfileResponse>(),
    },
    {
      id: 'llmProvider',
      label: 'Provider',
      width: '120px',
      render: createCategoryChipRenderer<ProfileResponse>('primary', 'outlined'),
    },
    {
      id: 'llmModel',
      label: 'Model',
      width: '180px',
      render: createMonospaceTextRenderer<ProfileResponse>(),
    },
    {
      id: 'temperature',
      label: 'Temperature',
      width: '120px',
      render: createCategoryChipRenderer<ProfileResponse>('secondary', 'outlined'),
    },
    {
      id: 'maxTokens',
      label: 'Max Tokens',
      width: '120px',
      render: (value?: number) => (
        value ? (
          <Typography variant="body2">
            {value.toLocaleString()}
          </Typography>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Unlimited
          </Typography>
        )
      ),
    },
    {
      id: 'createdAt',
      label: 'Created',
      width: '140px',
      render: (value: Date) => value ? format(value, 'MMM dd, yyyy') : '',
    },
  ];

  // Define CRUD configuration
  const config: CrudConfig<ProfileResponse> = {
    entityName: 'Profile',
    entityNamePlural: 'Profiles',
    columns,
    enableCreate: true,
    enableEdit: true,
    enableDelete: true,
    enableRefresh: true,
    pageSize: 10,
  };

  // Define service methods
  const service: CrudService<ProfileResponse, ProfileCreate, ProfileUpdate> = {
    list: async (page: number, pageSize: number) => {
      const response = await getSDK().profiles.listProfilesApiV1Profiles({
        limit: pageSize,
        offset: page * pageSize,
      });
      return {
        items: response.profiles || [],
        total: response.totalCount || 0,
      };
    },

    create: async (data: ProfileCreate) => {
      const response = await getSDK().profiles.createProfileApiV1Profiles(data);
      return response;
    },

    update: async (id: string, data: ProfileUpdate) => {
      const response = await getSDK().profiles.updateProfileApiV1ProfilesProfileId(
        id,
        data
      );
      return response;
    },

    delete: async (id: string) => {
      await getSDK().profiles.deleteProfileApiV1ProfilesProfileId(id);
    },
  };

  const getItemId = (item: ProfileResponse) => item.id || '';

  return (
    <PageLayout title="Profile Management">
      <CrudPageHeader
        entityName="Profile"
        onRefresh={() => crudTableRef.current?.handleRefresh()}
        onAdd={() => crudTableRef.current?.handleCreate()}
      />
      <CrudDataTable
        ref={crudTableRef}
        config={config}
        service={service}
        FormComponent={ProfileForm}
        getItemId={getItemId}
      />
    </PageLayout>
  );
};

export default ProfilesPage;
