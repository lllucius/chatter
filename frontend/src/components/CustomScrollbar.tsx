import React from 'react';
import { Scrollbar, ScrollbarProps } from 'react-scrollbars-custom';
import { useTheme } from '@mui/material/styles';

interface CustomScrollbarProps extends Omit<ScrollbarProps, 'style'> {
  style?: React.CSSProperties;
}

const CustomScrollbar: React.FC<CustomScrollbarProps> = ({ children, style, ...props }) => {
  const theme = useTheme();
  
  const scrollbarStyles = {
    // Track styles
    trackVertical: {
      position: 'absolute' as const,
      width: '8px',
      right: '0px',
      bottom: '0px',
      top: '0px',
      borderRadius: '4px',
      backgroundColor: theme.palette.mode === 'dark' 
        ? 'rgba(255, 255, 255, 0.1)' 
        : 'rgba(0, 0, 0, 0.1)',
    },
    trackHorizontal: {
      position: 'absolute' as const,
      height: '8px',
      left: '0px',
      right: '0px',
      bottom: '0px',
      borderRadius: '4px',
      backgroundColor: theme.palette.mode === 'dark' 
        ? 'rgba(255, 255, 255, 0.1)' 
        : 'rgba(0, 0, 0, 0.1)',
    },
    // Thumb styles
    thumbVertical: {
      position: 'relative' as const,
      display: 'block',
      width: '6px',
      minHeight: '20px',
      borderRadius: '3px',
      backgroundColor: theme.palette.mode === 'dark' 
        ? 'rgba(255, 255, 255, 0.4)' 
        : 'rgba(0, 0, 0, 0.4)',
      cursor: 'pointer',
      transition: 'background-color 0.2s ease',
      margin: '1px',
    },
    thumbHorizontal: {
      position: 'relative' as const,
      display: 'block',
      height: '6px',
      minWidth: '20px',
      borderRadius: '3px',
      backgroundColor: theme.palette.mode === 'dark' 
        ? 'rgba(255, 255, 255, 0.4)' 
        : 'rgba(0, 0, 0, 0.4)',
      cursor: 'pointer',
      transition: 'background-color 0.2s ease',
      margin: '1px',
    },
  };

  return (
    <Scrollbar
      style={{
        width: '100%',
        height: '100%',
        ...style,
      }}
      trackProps={{
        renderer: ({ elementRef, style: trackStyle, ...restProps }) => {
          const { className, ...validProps } = restProps;
          return (
            <div
              {...validProps}
              ref={elementRef}
              className={className}
              style={{
                ...trackStyle,
                ...(className?.includes('vertical') 
                  ? scrollbarStyles.trackVertical 
                  : scrollbarStyles.trackHorizontal),
              }}
            />
          );
        },
      }}
      thumbProps={{
        renderer: ({ elementRef, style: thumbStyle, ...restProps }) => {
          const { className, ...validProps } = restProps;
          return (
            <div
              {...validProps}
              ref={elementRef}
              className={className}
              style={{
                ...thumbStyle,
                ...(className?.includes('vertical')
                  ? scrollbarStyles.thumbVertical
                  : scrollbarStyles.thumbHorizontal),
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = theme.palette.mode === 'dark' 
                  ? 'rgba(255, 255, 255, 0.6)' 
                  : 'rgba(0, 0, 0, 0.6)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = theme.palette.mode === 'dark' 
                  ? 'rgba(255, 255, 255, 0.4)' 
                  : 'rgba(0, 0, 0, 0.4)';
              }}
            />
          );
        },
      }}
      // Auto-hide configuration
      trackClickBehavior="jump"
      autoHide
      autoHideTimeout={1000}
      autoHideDuration={200}
      {...props}
    >
      {children}
    </Scrollbar>
  );
};

export default CustomScrollbar;