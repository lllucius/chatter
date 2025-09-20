import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  ButtonGroup,
  Divider,
  Alert,
  Collapse,
  IconButton,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Description as DocumentIcon,
  Chat as ConversationIcon,
  Psychology as PromptIcon,
  TrendingUp as TrendingIcon,
  Lightbulb as RecommendationIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Star as StarIcon,
  AccessTime as RecentIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';

interface SearchResult {
  type: string;
  id: string;
  content: string;
  score: number;
  personalized_score: number;
  personalization_boost: number;
  personalization_factors: string[];
  metadata: Record<string, unknown>;
}

interface SearchRecommendation {
  type: string;
  title: string;
  description: string;
  suggested_queries?: string[];
  items?: Record<string, unknown>[];
}

interface TrendingContent {
  type: string;
  id: string;
  title: string;
  content: string;
  trending_score: number;
  metadata: Record<string, unknown>;
}

interface SearchResponse {
  results?: SearchResult[];
  recommendations?: SearchRecommendation[];
  user_context?: Record<string, unknown>;
}

interface TrendingResponse {
  trending_content?: TrendingContent[];
}

const IntelligentSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<
    'documents' | 'conversations' | 'prompts'
  >('documents');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [recommendations, setRecommendations] = useState<
    SearchRecommendation[]
  >([]);
  const [trendingContent, setTrendingContent] = useState<TrendingContent[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingTrending, setIsLoadingTrending] = useState(false);
  const [expandedRecommendations, setExpandedRecommendations] = useState<
    Set<number>
  >(new Set());
  const [userContext, setUserContext] = useState<Record<
    string,
    unknown
  > | null>(null);

  const performSearch = useCallback(async (query: string, type: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setRecommendations([]);
      return;
    }

    setIsSearching(true);
    try {
      const response =
        await getSDK().analytics.intelligentSearchApiV1AnalyticsRealTimeSearchIntelligent(
          {
            query: query.trim(),
            searchType: type,
            limit: 10,
            includeRecommendations: true,
          }
        );

      const searchResponse = response as SearchResponse;
      setSearchResults(searchResponse?.results || []);
      setRecommendations(searchResponse?.recommendations || []);
      setUserContext(searchResponse?.user_context || null);

      // Track search analytics (future implementation)
    } catch (error) {
      handleError(
        error,
        { source: 'IntelligentSearch.performSearch' },
        { fallbackMessage: 'Failed to perform intelligent search' }
      );
      setSearchResults([]);
      setRecommendations([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const loadTrendingContent = useCallback(async () => {
    setIsLoadingTrending(true);
    try {
      const response =
        await getSDK().analytics.getTrendingContentApiV1AnalyticsRealTimeSearchTrending(
          {
            limit: 10,
          }
        );
      const trendingResponse = response as TrendingResponse;
      setTrendingContent(trendingResponse?.trending_content || []);
    } catch (error) {
      handleError(
        error,
        { source: 'IntelligentSearch.loadTrendingContent' },
        { fallbackMessage: 'Failed to load trending content' }
      );
      setTrendingContent([]);
    } finally {
      setIsLoadingTrending(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch(searchQuery, searchType);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery, searchType, performSearch]);

  // Load trending content on mount
  useEffect(() => {
    loadTrendingContent();
  }, [loadTrendingContent]);

  const handleSearchTypeChange = (
    type: 'documents' | 'conversations' | 'prompts'
  ) => {
    setSearchType(type);
    if (searchQuery.trim()) {
      performSearch(searchQuery, type);
    }
  };

  const handleSuggestedQuery = (suggestedQuery: string) => {
    setSearchQuery(suggestedQuery);
    performSearch(suggestedQuery, searchType);
  };

  const toggleRecommendationExpansion = (index: number) => {
    setExpandedRecommendations((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'document':
      case 'document_chunk':
        return <DocumentIcon color="primary" />;
      case 'conversation':
        return <ConversationIcon color="secondary" />;
      case 'prompt':
        return <PromptIcon color="success" />;
      default:
        return <SearchIcon />;
    }
  };

  const getPersonalizationChips = (result: SearchResult) => {
    return result.personalization_factors?.map((factor, index) => (
      <Chip
        key={index}
        label={factor.replace('_', ' ').replace(':', ': ')}
        size="small"
        variant="outlined"
        color="primary"
        sx={{ mr: 0.5, mb: 0.5 }}
      />
    ));
  };

  const formatScore = (score: number) => Math.round(score * 100);

  return (
    <Box>
      {/* Search Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search documents, conversations, or prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  {isSearching ? (
                    <CircularProgress size={20} />
                  ) : (
                    <SearchIcon />
                  )}
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />

          {/* Search Type Buttons */}
          <ButtonGroup variant="outlined" size="small">
            <Button
              variant={searchType === 'documents' ? 'contained' : 'outlined'}
              onClick={() => handleSearchTypeChange('documents')}
              startIcon={<DocumentIcon />}
            >
              Documents
            </Button>
            <Button
              variant={
                searchType === 'conversations' ? 'contained' : 'outlined'
              }
              onClick={() => handleSearchTypeChange('conversations')}
              startIcon={<ConversationIcon />}
            >
              Conversations
            </Button>
            <Button
              variant={searchType === 'prompts' ? 'contained' : 'outlined'}
              onClick={() => handleSearchTypeChange('prompts')}
              startIcon={<PromptIcon />}
            >
              Prompts
            </Button>
          </ButtonGroup>

          {/* User Context Display */}
          {userContext && (
            <Box mt={2}>
              <Typography variant="caption" color="textSecondary">
                Personalized based on your preferences:
              </Typography>
              <Box display="flex" gap={1} mt={1} flexWrap="wrap">
                {Object.entries(userContext.preferred_content_types || {}).map(
                  ([type, preference]) => (
                    <Chip
                      key={type}
                      label={`${type}: ${Math.round((preference as number) * 100)}%`}
                      size="small"
                      variant="outlined"
                    />
                  )
                )}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      <Box display="flex" gap={3}>
        {/* Search Results */}
        <Box flex={2}>
          {searchResults.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Search Results ({searchResults.length})
                </Typography>
                <List>
                  {searchResults.map((result, index) => (
                    <React.Fragment key={result.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemIcon>
                          {getResultIcon(result.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle1">
                                {String(
                                  result.metadata?.title ||
                                    result.metadata?.name ||
                                    `${result.type} ${result.id}`
                                ) || 'Untitled'}
                              </Typography>
                              <Tooltip
                                title={`Relevance: ${formatScore(result.score)}% | Personalized: ${formatScore(result.personalized_score)}%`}
                              >
                                <Chip
                                  label={`${formatScore(result.personalized_score)}%`}
                                  size="small"
                                  color={
                                    result.personalization_boost > 0
                                      ? 'primary'
                                      : 'default'
                                  }
                                  icon={
                                    result.personalization_boost > 0 ? (
                                      <StarIcon />
                                    ) : undefined
                                  }
                                />
                              </Tooltip>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <>
                                <Typography
                                  variant="body2"
                                  color="textSecondary"
                                  paragraph
                                >
                                  {result.content.substring(0, 200)}
                                  {result.content.length > 200 ? '...' : ''}
                                </Typography>
                                {result.personalization_factors &&
                                  result.personalization_factors.length > 0 && (
                                    <Box>
                                      <Typography
                                        variant="caption"
                                        color="primary"
                                      >
                                        Personalized for you:
                                      </Typography>
                                      <Box mt={0.5}>
                                        {getPersonalizationChips(result)}
                                      </Box>
                                    </Box>
                                  )}
                                {result.metadata?.created_at && (
                                  <Typography
                                    variant="caption"
                                    color="textSecondary"
                                    display="block"
                                    mt={1}
                                  >
                                    Created:{' '}
                                    {format(
                                      new Date(
                                        typeof result.metadata?.created_at ===
                                        'string'
                                          ? result.metadata.created_at
                                          : new Date()
                                      ),
                                      'MMM d, yyyy'
                                    )}
                                  </Typography>
                                )}
                              </>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < searchResults.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <RecommendationIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Smart Recommendations
                </Typography>
                {recommendations.map((rec, index) => (
                  <Box key={index} mb={2}>
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="space-between"
                      sx={{ cursor: 'pointer' }}
                      onClick={() => toggleRecommendationExpansion(index)}
                    >
                      <Typography variant="subtitle2" color="primary">
                        {rec.title}
                      </Typography>
                      <IconButton size="small">
                        {expandedRecommendations.has(index) ? (
                          <CollapseIcon />
                        ) : (
                          <ExpandIcon />
                        )}
                      </IconButton>
                    </Box>
                    <Typography
                      variant="body2"
                      color="textSecondary"
                      gutterBottom
                    >
                      {rec.description}
                    </Typography>
                    <Collapse in={expandedRecommendations.has(index)}>
                      {rec.suggested_queries && (
                        <Box mt={1}>
                          <Typography variant="caption" color="textSecondary">
                            Try these searches:
                          </Typography>
                          <Box mt={0.5}>
                            {rec.suggested_queries.map((query, queryIndex) => (
                              <Button
                                key={queryIndex}
                                size="small"
                                variant="outlined"
                                onClick={() => handleSuggestedQuery(query)}
                                sx={{ mr: 1, mb: 0.5 }}
                              >
                                {query}
                              </Button>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Collapse>
                    {index < recommendations.length - 1 && (
                      <Divider sx={{ mt: 2 }} />
                    )}
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {searchQuery && searchResults.length === 0 && !isSearching && (
            <Alert severity="info">
              No results found for &ldquo;{searchQuery}&rdquo;. Try different
              keywords or check the recommendations below.
            </Alert>
          )}
        </Box>

        {/* Trending Content Sidebar */}
        <Box flex={1}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="between"
                mb={2}
              >
                <Typography variant="h6">
                  <TrendingIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Trending for You
                </Typography>
                {isLoadingTrending && <CircularProgress size={20} />}
              </Box>

              {trendingContent.length > 0 ? (
                <List dense>
                  {trendingContent.map((item, index) => (
                    <React.Fragment key={item.id}>
                      <ListItem
                        component="button"
                        onClick={() => {
                          setSearchQuery(item.title);
                          setSearchType('documents');
                        }}
                      >
                        <ListItemIcon>
                          <RecentIcon color="action" />
                        </ListItemIcon>
                        <ListItemText
                          primary={item.title}
                          secondary={
                            <Box>
                              <Typography
                                variant="caption"
                                color="textSecondary"
                              >
                                {item.content.substring(0, 50)}...
                              </Typography>
                              <Chip
                                label={`${Math.round(item.trending_score * 100)}% trending`}
                                size="small"
                                color="primary"
                                variant="outlined"
                                sx={{ ml: 1 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < trendingContent.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No trending content available yet.
                </Typography>
              )}

              <Button
                fullWidth
                variant="outlined"
                startIcon={<TrendingIcon />}
                onClick={loadTrendingContent}
                sx={{ mt: 2 }}
                disabled={isLoadingTrending}
              >
                Refresh Trending
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default IntelligentSearch;
