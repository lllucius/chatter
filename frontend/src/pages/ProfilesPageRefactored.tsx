import React from 'react';
import { Typography } from '@mui/material';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import ProfileForm from '../components/ProfileForm';
import { 
  createNameWithDescriptionRenderer, 
  createCategoryChipRenderer,
  createMonospaceTextRenderer 
} from '../components/CrudRenderers';
import { chatterSDK } from '../services/chatter-sdk';
import { ProfileResponse, ProfileCreate, ProfileUpdate } from '../sdk';

const ProfilesPageRefactored: React.FC = () => {
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
      render: (value: number) => (
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
      render: (value) => value ? format(new Date(value), 'MMM dd, yyyy') : '',
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
    list: async () => {
      const response = await chatterSDK.profiles.listProfilesApiV1ProfilesGet({});
      return {
        items: response.profiles || [],
        total: response.totalCount || 0,
      };
    },

    create: async (data: ProfileCreate) => {
      const response = await chatterSDK.profiles.createProfileApiV1ProfilesPost({
        profileCreate: data,
      });
      return response;
    },

    update: async (id: string, data: ProfileUpdate) => {
      const response = await chatterSDK.profiles.updateProfileApiV1ProfilesProfileIdPut({
        profileId: id,
        profileUpdate: data,
      });
      return response;
    },

    delete: async (id: string) => {
      await chatterSDK.profiles.deleteProfileApiV1ProfilesProfileIdDelete({
        profileId: id,
      });
    },
  };

  const getItemId = (item: ProfileResponse) => item.id || '';

  return (
    <PageLayout title="Profile Management">
      <CrudDataTable
        config={config}
        service={service}
        FormComponent={ProfileForm}
        getItemId={getItemId}
      />
    </PageLayout>
  );
};

export default ProfilesPageRefactored;