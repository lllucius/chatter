import React, { useEffect } from 'react';
import SimpleBarReact from 'simplebar-react';
import { useTheme } from '@mui/material/styles';
import 'simplebar-react/dist/simplebar.min.css';

interface CustomScrollbarProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

const CustomScrollbar: React.FC<CustomScrollbarProps> = ({ children, style, className, ...props }) => {
  const theme = useTheme();

  useEffect(() => {
    // Create custom CSS for theming SimpleBar
    const styleId = 'simplebar-theme';
    let styleElement = document.getElementById(styleId) as HTMLStyleElement;
    
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      document.head.appendChild(styleElement);
    }

    const isDark = theme.palette.mode === 'dark';
    const trackBg = isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(0, 0, 0, 0.15)';
    const thumbBg = isDark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)';
    const thumbHoverBg = isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.8)';

    styleElement.textContent = `
      .simplebar-track.simplebar-vertical {
        width: 6px !important;
        background-color: ${trackBg} !important;
        border-radius: 3px !important;
        right: 0px !important;
      }
      
      .simplebar-track.simplebar-horizontal {
        height: 6px !important;
        background-color: ${trackBg} !important;
        border-radius: 3px !important;
        bottom: 0px !important;
      }
      
      .simplebar-scrollbar::before {
        background-color: ${thumbBg} !important;
        border-radius: 2px !important;
        transition: background-color 0.2s ease !important;
      }
      
      .simplebar-track.simplebar-vertical .simplebar-scrollbar::before {
        width: 4px !important;
        margin: 1px !important;
      }
      
      .simplebar-track.simplebar-horizontal .simplebar-scrollbar::before {
        height: 4px !important;
        margin: 1px !important;
      }
      
      .simplebar-scrollbar:hover::before {
        background-color: ${thumbHoverBg} !important;
      }
    `;
  }, [theme.palette.mode]);

  return (
    <SimpleBarReact
      className={className}
      style={{
        width: '100%',
        height: '100%',
        ...style,
      }}
      options={{
        autoHide: false,
      }}
      {...props}
    >
      {children}
    </SimpleBarReact>
  );
};

export default CustomScrollbar;