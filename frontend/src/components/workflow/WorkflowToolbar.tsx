import React from 'react';
import { Button, ButtonGroup, Tooltip } from '@mui/material';
import {
  Save as SaveIcon,
  Visibility as ValidateIcon,
  HistoryEdu as TemplateIcon,
  GetApp as ExampleIcon,
  PlayArrow as StartIcon,
  SmartToy as ModelIcon,
  Build as ToolIcon,
  Memory as MemoryIcon,
  Search as RetrievalIcon,
  CallSplit as ConditionalIcon,
  Loop as LoopIcon,
  Storage as VariableIcon,
  Error as ErrorHandlerIcon,
  Schedule as DelayIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
  GridOn as GridIcon,
  Settings as PropertiesIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';

interface ToolbarButtonConfig {
  icon: React.ReactElement;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'success' | 'error';
  title?: string;
}

interface ToolbarSectionProps {
  buttons: ToolbarButtonConfig[];
  size?: 'small' | 'medium' | 'large';
}

const ToolbarSection: React.FC<ToolbarSectionProps> = ({ buttons, size = 'small' }) => {
  return (
    <ButtonGroup size={size} sx={{ mr: 2 }}>
      {buttons.map((button, index) => (
        <Tooltip key={index} title={button.title || button.label}>
          <Button
            startIcon={button.icon}
            onClick={button.onClick}
            disabled={button.disabled}
            variant={button.variant || 'outlined'}
            color={button.color || 'primary'}
            title={button.title}
          >
            {button.label}
          </Button>
        </Tooltip>
      ))}
    </ButtonGroup>
  );
};

interface WorkflowToolbarProps {
  // Main actions
  onSave: () => void;
  onValidate: () => void;
  onShowTemplates: () => void;
  onShowExamples: (event: React.MouseEvent<HTMLElement>) => void;
  
  // Node creation
  onAddNode: (type: string) => void;
  
  // Edit actions
  onUndo: () => void;
  onRedo: () => void;
  onCopy: () => void;
  onPaste: () => void;
  onDeleteSelected: () => void;
  
  // View options
  snapToGrid: boolean;
  onToggleSnap: () => void;
  onShowProperties: () => void;
  onShowAnalytics: () => void;
  
  // State
  selectedNode: any;
  clipboard: any;
  historyIndex: number;
  historyLength: number;
  showPropertiesPanel: boolean;
  sidePanelTab: 'properties' | 'analytics';
}

const WorkflowToolbar: React.FC<WorkflowToolbarProps> = ({
  onSave,
  onValidate,
  onShowTemplates,
  onShowExamples,
  onAddNode,
  onUndo,
  onRedo,
  onCopy,
  onPaste,
  onDeleteSelected,
  snapToGrid,
  onToggleSnap,
  onShowProperties,
  onShowAnalytics,
  selectedNode,
  clipboard,
  historyIndex,
  historyLength,
  showPropertiesPanel,
  sidePanelTab,
}) => {
  const mainActions: ToolbarButtonConfig[] = [
    { icon: <SaveIcon />, label: 'Save', onClick: onSave, title: 'Save Workflow (Ctrl+S)' },
    { icon: <ValidateIcon />, label: 'Validate', onClick: onValidate, title: 'Validate Workflow' },
    { icon: <TemplateIcon />, label: 'Templates', onClick: onShowTemplates, title: 'Workflow Templates' },
    { icon: <ExampleIcon />, label: 'Examples', onClick: onShowExamples, title: 'Example Workflows' },
  ];

  const nodeTypes: ToolbarButtonConfig[] = [
    { icon: <StartIcon />, label: 'Start', onClick: () => onAddNode('start'), color: 'success', title: 'Add Start Node' },
    { icon: <ModelIcon />, label: 'Model', onClick: () => onAddNode('model'), color: 'secondary', title: 'Add Model Node' },
    { icon: <ToolIcon />, label: 'Tool', onClick: () => onAddNode('tool'), color: 'secondary', title: 'Add Tool Node' },
    { icon: <MemoryIcon />, label: 'Memory', onClick: () => onAddNode('memory'), color: 'secondary', title: 'Add Memory Node' },
    { icon: <RetrievalIcon />, label: 'Retrieval', onClick: () => onAddNode('retrieval'), color: 'secondary', title: 'Add Retrieval Node' },
    { icon: <ConditionalIcon />, label: 'Conditional', onClick: () => onAddNode('conditional'), color: 'secondary', title: 'Add Conditional Node' },
    { icon: <LoopIcon />, label: 'Loop', onClick: () => onAddNode('loop'), color: 'secondary', title: 'Add Loop Node' },
    { icon: <VariableIcon />, label: 'Variable', onClick: () => onAddNode('variable'), color: 'secondary', title: 'Add Variable Node' },
    { icon: <ErrorHandlerIcon />, label: 'Error', onClick: () => onAddNode('errorHandler'), color: 'secondary', title: 'Add Error Handler Node' },
    { icon: <DelayIcon />, label: 'Delay', onClick: () => onAddNode('delay'), color: 'secondary', title: 'Add Delay Node' },
  ];

  const editActions: ToolbarButtonConfig[] = [
    { icon: <UndoIcon />, label: 'Undo', onClick: onUndo, disabled: historyIndex <= 0, title: 'Undo (Ctrl+Z)' },
    { icon: <RedoIcon />, label: 'Redo', onClick: onRedo, disabled: historyIndex >= historyLength - 1, title: 'Redo (Ctrl+Shift+Z)' },
    { icon: <CopyIcon />, label: 'Copy', onClick: onCopy, disabled: !selectedNode, title: 'Copy (Ctrl+C)' },
    { icon: <PasteIcon />, label: 'Paste', onClick: onPaste, disabled: !clipboard, title: 'Paste (Ctrl+V)' },
  ];

  const utilityActions: ToolbarButtonConfig[] = [
    { icon: <GridIcon />, label: 'Grid', onClick: onToggleSnap, variant: snapToGrid ? 'contained' : 'outlined', title: 'Toggle Grid Snap' },
    { 
      icon: <PropertiesIcon />, 
      label: 'Properties', 
      onClick: onShowProperties, 
      variant: showPropertiesPanel && sidePanelTab === 'properties' ? 'contained' : 'outlined',
      title: 'Show Properties Panel' 
    },
    { 
      icon: <AnalyticsIcon />, 
      label: 'Analytics', 
      onClick: onShowAnalytics, 
      variant: showPropertiesPanel && sidePanelTab === 'analytics' ? 'contained' : 'outlined',
      title: 'Show Analytics Panel' 
    },
  ];

  return (
    <>
      {/* Main Actions */}
      <ToolbarSection buttons={mainActions} />
      
      {/* Node Types */}
      <ToolbarSection buttons={nodeTypes} />
      
      {/* Edit Controls */}
      <ToolbarSection buttons={editActions} />
      
      {/* Utility Controls */}
      <ToolbarSection buttons={utilityActions} />
    </>
  );
};

export default WorkflowToolbar;