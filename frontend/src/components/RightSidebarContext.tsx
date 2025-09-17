import React, { createContext, useContext, useState, ReactNode } from 'react';

interface RightSidebarContextValue {
  panelContent: ReactNode | null;
  setPanelContent: (content: ReactNode | null) => void;
  clearPanelContent: () => void;

  title: string;
  setTitle: (title: string) => void;

  open: boolean;
  setOpen: (open: boolean) => void;

  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

const RightSidebarContext = createContext<RightSidebarContextValue | undefined>(
  undefined
);

export const RightSidebarProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [panelContent, setPanelContent] = useState<ReactNode | null>(null);
  const [title, setTitle] = useState<string>('Panel');
  const [open, setOpen] = useState<boolean>(false);
  const [collapsed, setCollapsed] = useState<boolean>(false);

  const clearPanelContent = () => setPanelContent(null);

  return (
    <RightSidebarContext.Provider
      value={{
        panelContent,
        setPanelContent,
        clearPanelContent,
        title,
        setTitle,
        open,
        setOpen,
        collapsed,
        setCollapsed,
      }}
    >
      {children}
    </RightSidebarContext.Provider>
  );
};

export const useRightSidebar = (): RightSidebarContextValue => {
  const ctx = useContext(RightSidebarContext);
  if (!ctx) {
    throw new Error(
      'useRightSidebar must be used within a RightSidebarProvider'
    );
  }
  return ctx;
};
