# Message Rating Feature

This document describes the newly implemented message rating feature that allows users to rate assistant responses and provides analytics on those ratings.

## Overview

The message rating feature enables users to rate assistant messages on a scale of 0.0 to 5.0. These ratings are persisted to the database and included in analytics dashboards for insights into response quality.

## API Endpoints

### Rate a Message

**PATCH** `/api/v1/conversations/{conversation_id}/messages/{message_id}/rating`

Rate an assistant message with a value between 0.0 and 5.0.

**Request Body:**
```json
{
  "rating": 4.5
}
```

**Response:**
```json
{
  "message": "Message rating updated successfully",
  "rating": 4.33,
  "rating_count": 3
}
```

**Response Fields:**
- `message`: Success message
- `rating`: Current average rating for the message
- `rating_count`: Total number of ratings for the message

### Get Analytics with Ratings

**GET** `/api/v1/analytics/conversations`

Returns conversation statistics including message rating metrics.

**Response includes new rating fields:**
```json
{
  // ... existing fields ...
  "total_ratings": 156,
  "avg_message_rating": 4.2,
  "messages_with_ratings": 42,
  "rating_distribution": {
    "5_stars": 18,
    "4_stars": 15,
    "3_stars": 6,
    "2_stars": 2,
    "1_star": 1
  }
}
```

## Database Schema

### Messages Table

Two new columns have been added to the `messages` table:

- `rating` (FLOAT): Average rating for the message (0.0-5.0), nullable
- `rating_count` (INTEGER): Number of ratings received, default 0

### Constraints

- `rating` must be between 0.0 and 5.0 if not null
- `rating_count` must be >= 0

## Rating Calculation

When a user rates a message:

1. **First rating**: `rating` = submitted rating, `rating_count` = 1
2. **Subsequent ratings**: New average is calculated as:
   ```
   new_rating = (current_rating * rating_count + new_rating) / (rating_count + 1)
   rating_count = rating_count + 1
   ```

## Frontend Integration

The frontend `EnhancedMessage` component already includes rating UI for assistant messages. It should call the rating endpoint when a user submits a rating:

```typescript
const handleRatingChange = async (messageId: string, rating: number) => {
  try {
    const response = await fetch(
      `/api/v1/conversations/${conversationId}/messages/${messageId}/rating`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating })
      }
    );
    const result = await response.json();
    // Update UI with new average rating
  } catch (error) {
    console.error('Failed to rate message:', error);
  }
};
```

## Analytics Use Cases

The rating analytics enable several insights:

1. **Quality Monitoring**: Track average message rating over time
2. **User Satisfaction**: Understand how users perceive assistant responses
3. **Model Comparison**: Compare ratings between different LLM models/providers
4. **Performance Trends**: Identify improvement or degradation in response quality
5. **Content Optimization**: Find highly-rated responses for training or examples

## Migration

Run the database migration to add rating columns:

```bash
alembic upgrade head
```

The migration adds the rating columns with proper constraints and default values.

## Error Handling

- **400 Bad Request**: Invalid rating value (outside 0.0-5.0 range)
- **401 Unauthorized**: User not authenticated
- **404 Not Found**: Message or conversation not found
- **403 Forbidden**: User doesn't have access to the conversation

## Testing

Run the rating tests:

```bash
pytest tests/test_message_rating.py -v
```

The tests cover:
- Schema validation
- Rating calculation logic
- Error handling
- API response formats