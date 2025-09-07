import React from 'react';
import { Chip, Typography, Box } from '@mui/material';
import { format } from 'date-fns';
import PageLayout from '../components/PageLayout';
import CrudDataTable, { CrudConfig, CrudService, CrudColumn } from '../components/CrudDataTable';
import ProfileForm from '../components/ProfileForm';
import { chatterSDK } from '../services/chatter-sdk';
import { ProfileResponse, ProfileCreate, ProfileUpdate } from '../sdk';

const ProfilesPageRefactored: React.FC = () => {
  // Define columns
  const columns: CrudColumn<ProfileResponse>[] = [
    {
      id: 'name',
      label: 'Name',
      width: '200px',
      render: (value, item) => (
        <Box>
          <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
            {value}
          </Typography>
          {item.description && (
            <Typography variant="body2" color="text.secondary">
              {item.description}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      id: 'llm_provider',
      label: 'Provider',
      width: '120px',
      render: (value) => (
        <Chip
          label={value}
          color="primary"
          variant="outlined"
          size="small"
        />
      ),
    },
    {
      id: 'llm_model',
      label: 'Model',
      width: '180px',
      render: (value) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'temperature',
      label: 'Temperature',
      width: '120px',
      render: (value) => (
        <Chip
          label={value}
          color="secondary"
          variant="outlined"
          size="small"
        />
      ),
    },
    {
      id: 'max_tokens',
      label: 'Max Tokens',
      width: '120px',
      render: (value) => (
        value ? (
          <Typography variant="body2">
            {value.toLocaleString()}
          </Typography>
        ) : (
          '-'
        )
      ),
    },
    {
      id: 'created_at',
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
    list: async (page: number, pageSize: number) => {
      const response = await chatterSDK.profiles.listProfilesApiV1ProfilesGet({});
      return {
        items: response.data.profiles || [],
        total: response.data.profiles?.length || 0,
      };
    },

    create: async (data: ProfileCreate) => {
      const response = await chatterSDK.profiles.createProfileApiV1ProfilesPost({
        profileCreate: data,
      });
      return response.data;
    },

    update: async (id: string, data: ProfileUpdate) => {
      const response = await chatterSDK.profiles.updateProfileApiV1ProfilesProfileIdPut({
        profileId: id,
        profileUpdate: data,
      });
      return response.data;
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