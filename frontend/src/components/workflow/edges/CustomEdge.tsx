import React from 'react';
import {
  EdgeProps,
  EdgeLabelRenderer,
  getBezierPath,
  BaseEdge,
} from '@xyflow/react';
import { Chip } from '@mui/material';

const CustomEdge: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  style = {},
  markerEnd,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isConditional = data?.condition || data?.label;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: selected ? '#2196f3' : isConditional ? '#ff9800' : '#666',
          strokeWidth: selected ? 3 : 2,
          strokeDasharray: isConditional ? '5,5' : undefined,
        }}
      />

      {isConditional && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="nodrag nopan"
          >
            <Chip
              label={String(data?.label || data?.condition || 'condition')}
              size="small"
              color="warning"
              sx={{
                fontSize: '0.7rem',
                height: '20px',
                bgcolor: 'rgba(255, 152, 0, 0.9)',
                color: 'white',
              }}
            />
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
};

export default CustomEdge;
