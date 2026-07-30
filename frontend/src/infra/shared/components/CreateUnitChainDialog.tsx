import { useState, useEffect, useCallback } from 'react';
import { useI18n } from '../../locales/I18nContext';
import { SearchableCombobox, type SelectOption } from './SearchableCombobox';
import type { UnitType } from '../../../modules/master/types';

interface UnitItem {
    id: number;
    name: string;
    code: string;
    description?: string | null;
    parent_id?: number | null;
}

interface CreateUnitChainDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (chain: { chain: Array<{ type: UnitType; id?: number; name: string; code: string; description?: string }> }) => Promise<void>;
    existingForces: UnitItem[];
    existingCommands: UnitItem[];
    existingBattalions: UnitItem[];
    existingUnits: UnitItem[];
    closeOnBackdropClick?: boolean;
}

interface UnitLevel {
    id: number | null;
    name: string;
    code: string;
    description: string;
    isCreating: boolean;
}

interface DialogState {
    force: UnitLevel;
    command: UnitLevel;
    battalion: UnitLevel;
    unit: UnitLevel;
    hasUnsavedChanges: boolean;
    isSubmitting: boolean;
    error: string | null;
}

const EMPTY_LEVEL: UnitLevel = {
    id: null,
    name: '',
    code: '',
    description: '',
    isCreating: false,
};

export const CreateUnitChainDialog: React.FC<CreateUnitChainDialogProps> = ({
    isOpen,
    onClose,
    onSubmit,
    existingForces,
    existingCommands,
    existingBattalions,
    existingUnits,
    closeOnBackdropClick = false,
}) => {
    const { t } = useI18n();
    
    const [state, setState] = useState<DialogState>({
        force: { ...EMPTY_LEVEL },
        command: { ...EMPTY_LEVEL },
        battalion: { ...EMPTY_LEVEL },
        unit: { ...EMPTY_LEVEL },
        hasUnsavedChanges: false,
        isSubmitting: false,
        error: null,
    });

    const showCommand = state.force.id !== null || state.force.isCreating;
    const showBattalion = state.command.id !== null || state.command.isCreating;
    const showUnit = state.battalion.id !== null || state.battalion.isCreating;

    useEffect(() => {
        const hasChanges = 
            state.force.name !== '' || state.force.code !== '' ||
            state.command.name !== '' || state.command.code !== '' ||
            state.battalion.name !== '' || state.battalion.code !== '' ||
            state.unit.name !== '' || state.unit.code !== '' ||
            state.force.id !== null || state.command.id !== null || 
            state.battalion.id !== null || state.unit.id !== null;
        
        setState(prev => ({ ...prev, hasUnsavedChanges: hasChanges }));
    }, [state.force, state.command, state.battalion, state.unit]);

    useEffect(() => {
        if (!isOpen || !closeOnBackdropClick) return;
        
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                handleClose();
            }
        };
        
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, closeOnBackdropClick, state.hasUnsavedChanges]);

    const handleClose = useCallback(() => {
        if (state.hasUnsavedChanges) {
            const confirmed = window.confirm(t('nav.master.dialogs.unsavedChanges') || 'You have unsaved changes. Discard?');
            if (!confirmed) return;
        }
        setState(prev => ({
            ...prev,
            force: { ...EMPTY_LEVEL },
            command: { ...EMPTY_LEVEL },
            battalion: { ...EMPTY_LEVEL },
            unit: { ...EMPTY_LEVEL },
            error: null,
        }));
        onClose();
    }, [state.hasUnsavedChanges, onClose, t]);

    const updateLevel = useCallback(<K extends 'force' | 'command' | 'battalion' | 'unit'>(
        level: K,
        updates: Partial<UnitLevel>
    ) => {
        setState(prev => ({
            ...prev,
            [level]: { ...prev[level], ...updates },
        }));
    }, []);

    const handleForceSelect = useCallback((selected: { id: number; name: string; code: string; description?: string | null } | null) => {
        if (selected) {
            updateLevel('force', { 
                id: selected.id, 
                name: selected.name, 
                code: selected.code,
                description: selected.description || '',
                isCreating: false 
            });
        } else {
            updateLevel('force', { id: null, name: '', code: '', description: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleForceCreate = useCallback((code: string) => {
        updateLevel('force', { code, isCreating: true, id: null, name: '', description: '' });
    }, [updateLevel]);

    const handleCommandSelect = useCallback((selected: { id: number; name: string; code: string; description?: string | null } | null) => {
        if (selected) {
            updateLevel('command', { 
                id: selected.id, 
                name: selected.name, 
                code: selected.code,
                description: selected.description || '',
                isCreating: false 
            });
        } else {
            updateLevel('command', { id: null, name: '', code: '', description: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleCommandCreate = useCallback((code: string) => {
        updateLevel('command', { code, isCreating: true, id: null, name: '', description: '' });
    }, [updateLevel]);

    const handleBattalionSelect = useCallback((selected: { id: number; name: string; code: string; description?: string | null } | null) => {
        if (selected) {
            updateLevel('battalion', { 
                id: selected.id, 
                name: selected.name, 
                code: selected.code,
                description: selected.description || '',
                isCreating: false 
            });
        } else {
            updateLevel('battalion', { id: null, name: '', code: '', description: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleBattalionCreate = useCallback((code: string) => {
        updateLevel('battalion', { code, isCreating: true, id: null, name: '', description: '' });
    }, [updateLevel]);

    const handleUnitSelect = useCallback((selected: { id: number; name: string; code: string } | null) => {
        if (selected) {
            updateLevel('unit', { 
                id: selected.id, 
                name: selected.name, 
                code: selected.code,
                description: '',
                isCreating: false 
            });
        } else {
            updateLevel('unit', { id: null, name: '', code: '', description: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleUnitCreate = useCallback((code: string) => {
        updateLevel('unit', { code, isCreating: true, id: null, name: '', description: '' });
    }, [updateLevel]);

    const validate = (): boolean => {
        const errors: string[] = [];
        
        // Force is always required - only code is mandatory
        if (state.force.id === null && !state.force.isCreating) {
            errors.push('Force is required');
        } else if (state.force.isCreating && !state.force.code.trim()) {
            errors.push('Force code is required');
        }
        
        // Command is optional - only validate if user started interacting with it
        if (showCommand && (state.command.id !== null || state.command.isCreating || state.command.name !== '' || state.command.code !== '')) {
            if (state.command.id === null && !state.command.isCreating) {
                errors.push('Command is required');
            } else if (state.command.isCreating && !state.command.code.trim()) {
                errors.push('Command code is required');
            }
        }
        
        // Battalion is optional - only validate if user started interacting with it
        if (showBattalion && (state.battalion.id !== null || state.battalion.isCreating || state.battalion.name !== '' || state.battalion.code !== '')) {
            if (state.battalion.id === null && !state.battalion.isCreating) {
                errors.push('Battalion is required');
            } else if (state.battalion.isCreating && !state.battalion.code.trim()) {
                errors.push('Battalion code is required');
            }
        }
        
        // Unit is optional - only validate if user started interacting with it
        if (showUnit && (state.unit.id !== null || state.unit.isCreating || state.unit.name !== '' || state.unit.code !== '')) {
            if (state.unit.id === null && !state.unit.isCreating) {
                errors.push('Unit is required');
            } else if (state.unit.isCreating && !state.unit.code.trim()) {
                errors.push('Unit code is required');
            }
        }
        
        if (errors.length > 0) {
            setState(prev => ({ ...prev, error: errors.join(', ') }));
            return false;
        }
        
        return true;
    };

    const buildChain = () => {
        const chain: Array<{ type: UnitType; id?: number; name: string; code: string; description?: string }> = [];
        
        if (state.force.isCreating) {
            chain.push({
                type: 'force',
                name: state.force.name,
                code: state.force.code,
                description: state.force.description || undefined,
            });
        } else if (state.force.id) {
            chain.push({
                type: 'force',
                id: state.force.id,
                name: state.force.name,
                code: state.force.code,
                description: state.force.description || undefined,
            });
        }
        
        if (showCommand) {
            if (state.command.isCreating) {
                chain.push({
                    type: 'command',
                    name: state.command.name,
                    code: state.command.code,
                    description: state.command.description || undefined,
                });
            } else if (state.command.id) {
                chain.push({
                    type: 'command',
                    id: state.command.id,
                    name: state.command.name,
                    code: state.command.code,
                    description: state.command.description || undefined,
                });
            }
        }
        
        if (showBattalion) {
            if (state.battalion.isCreating) {
                chain.push({
                    type: 'battalion',
                    name: state.battalion.name,
                    code: state.battalion.code,
                    description: state.battalion.description || undefined,
                });
            } else if (state.battalion.id) {
                chain.push({
                    type: 'battalion',
                    id: state.battalion.id,
                    name: state.battalion.name,
                    code: state.battalion.code,
                    description: state.battalion.description || undefined,
                });
            }
        }
        
        if (showUnit) {
            if (state.unit.isCreating) {
                chain.push({
                    type: 'unit',
                    name: state.unit.name,
                    code: state.unit.code,
                    description: state.unit.description || undefined,
                });
            } else if (state.unit.id) {
                chain.push({
                    type: 'unit',
                    id: state.unit.id,
                    name: state.unit.name,
                    code: state.unit.code,
                    description: state.unit.description || undefined,
                });
            }
        }
        
        return { chain };
    };

    const handleSubmit = async () => {
        if (!validate()) return;
        
        setState(prev => ({ ...prev, isSubmitting: true, error: null }));
        
        try {
            const chain = buildChain();
            await onSubmit(chain);
            setState(prev => ({
                ...prev,
                force: { ...EMPTY_LEVEL },
                command: { ...EMPTY_LEVEL },
                battalion: { ...EMPTY_LEVEL },
                unit: { ...EMPTY_LEVEL },
                hasUnsavedChanges: false,
            }));
            onClose();
        } catch (err) {
            setState(prev => ({
                ...prev,
                error: err instanceof Error ? err.message : 'Failed to create units',
            }));
        } finally {
            setState(prev => ({ ...prev, isSubmitting: false }));
        }
    };

    const getSummary = () => {
        const parts: string[] = [];
        
        if (state.force.id || state.force.isCreating) {
            parts.push(`${state.force.name || 'Force'} (${state.force.code})`);
        }
        if (showCommand && (state.command.id || state.command.isCreating)) {
            parts.push(`${state.command.name || 'Command'} (${state.command.code})`);
        }
        if (showBattalion && (state.battalion.id || state.battalion.isCreating)) {
            parts.push(`${state.battalion.name || 'Battalion'} (${state.battalion.code})`);
        }
        if (showUnit && (state.unit.id || state.unit.isCreating)) {
            parts.push(`${state.unit.name || 'Unit'} (${state.unit.code})`);
        }
        
        return parts.join(' > ');
    };

    const hasNewItems = state.force.isCreating || state.command.isCreating || state.battalion.isCreating || state.unit.isCreating;
    const buttonText = hasNewItems 
        ? t('nav.master.dialogs.createUnits') || 'Create Units'
        : t('nav.master.dialogs.modifyUnit') || 'Modify Unit';

    if (!isOpen) return null;

    // Map existing items to combobox options (code as value for searching)
    const forceOptions: SelectOption[] = existingForces
        .map(f => ({ 
            id: f.id, 
            value: f.code,
            meta: { name: f.name, code: f.code, description: f.description }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    // Filter commands by selected force
    const commandOptions: SelectOption[] = existingCommands
        .filter(c => state.force.id ? c.parent_id === state.force.id : true)
        .map(c => ({ 
            id: c.id, 
            value: c.code,
            meta: { name: c.name, code: c.code, description: c.description }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    // Filter battalions by selected command
    const battalionOptions: SelectOption[] = existingBattalions
        .filter(b => state.command.id ? b.parent_id === state.command.id : true)
        .map(b => ({ 
            id: b.id, 
            value: b.code,
            meta: { name: b.name, code: b.code, description: b.description }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    // Filter units by selected battalion
    const unitOptions: SelectOption[] = existingUnits
        .filter(u => state.battalion.id ? u.parent_id === state.battalion.id : true)
        .map(u => ({ 
            id: u.id, 
            value: u.code,
            meta: { name: u.name, code: u.code }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));

    const codeInputClass = 'w-24 px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20';
    const nameInputClass = 'w-48 px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20';
    const descInputClass = 'flex-1 px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20';

    const renderLevelRow = (
        label: string,
        level: UnitLevel,
        options: SelectOption[],
        onSelect: (selected: { id: number; name: string; code: string; description?: string | null } | null) => void,
        onCreate: (code: string) => void,
        levelKey: 'force' | 'command' | 'battalion' | 'unit'
    ) => (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-primary">{label} *</span>
                {level.isCreating && <span className="text-xs text-accent">Creating new</span>}
            </div>
            <div className="flex items-center gap-2">
                <SearchableCombobox
                    options={options}
                    placeholder={`Type code or search (e.g., "JAC")`}
                    selected={level.id ? { id: level.id, value: level.code } : null}
                    onChange={(selected) => {
                        if (selected) {
                            const selectedWithMeta = selected as SelectOption & { meta?: { name?: string; code?: string; description?: string | null } };
                            const name = (selectedWithMeta.meta?.name) || selected.value;
                            const code = (selectedWithMeta.meta?.code) || selected.value;
                            const description = selectedWithMeta.meta?.description || null;
                            onSelect({ id: selected.id as number, name, code, description });
                        } else {
                            onSelect(null);
                        }
                    }}
                    onAddNew={onCreate}
                    className="w-48"
                />
                <input
                    type="text"
                    placeholder="Name *"
                    value={level.name}
                    onChange={(e) => updateLevel(levelKey, { name: e.target.value })}
                    className={nameInputClass}
                />
                <input
                    type="text"
                    placeholder="Description (optional)"
                    value={level.description}
                    onChange={(e) => updateLevel(levelKey, { description: e.target.value })}
                    className={descInputClass}
                />
            </div>
        </div>
    );

    const renderUnitRow = () => (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-primary">Unit *</span>
                {state.unit.isCreating && <span className="text-xs text-accent">Creating new</span>}
            </div>
            <div className="flex items-center gap-2">
                <input
                    type="text"
                    placeholder="Code *"
                    value={state.unit.code}
                    onChange={(e) => {
                        const code = e.target.value;
                        if (code && !state.unit.isCreating && !state.unit.id) {
                            updateLevel('unit', { code, isCreating: true });
                        } else {
                            updateLevel('unit', { code });
                        }
                    }}
                    className={codeInputClass}
                />
                <input
                    type="text"
                    placeholder="Name *"
                    value={state.unit.name}
                    onChange={(e) => updateLevel('unit', { name: e.target.value })}
                    className={nameInputClass}
                />
                <input
                    type="text"
                    placeholder="Description (optional)"
                    value={state.unit.description}
                    onChange={(e) => updateLevel('unit', { description: e.target.value })}
                    className={descInputClass}
                />
            </div>
        </div>
    );

    return (
        <div 
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" 
            onClick={closeOnBackdropClick ? handleClose : undefined}
        >
            <div 
                className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-4xl"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="px-6 py-4 border-b border-bd flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-primary">{t('nav.master.dialogs.createUnit') || 'Create Unit'}</h2>
                    <button
                        onClick={handleClose}
                        className="p-2 rounded-lg hover:bg-surface-2 transition-colors"
                        title="Close"
                    >
                        <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    {renderLevelRow(
                        'Force',
                        state.force,
                        forceOptions,
                        handleForceSelect,
                        handleForceCreate,
                        'force'
                    )}

                    {showCommand && renderLevelRow(
                        'Command',
                        state.command,
                        commandOptions,
                        handleCommandSelect,
                        handleCommandCreate,
                        'command'
                    )}

                    {showBattalion && renderLevelRow(
                        'Battalion',
                        state.battalion,
                        battalionOptions,
                        handleBattalionSelect,
                        handleBattalionCreate,
                        'battalion'
                    )}

                    {showUnit && renderUnitRow()}

                    {state.error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-sm text-red-500">{state.error}</p>
                        </div>
                    )}
                </div>

                {(state.force.id || state.force.isCreating || state.command.id || state.command.isCreating || 
                  state.battalion.id || state.battalion.isCreating || state.unit.id || state.unit.isCreating) && (
                    <div className="px-6 py-4 border-t border-bd bg-surface-2">
                        <p className="text-sm font-semibold text-secondary mb-2">
                            {hasNewItems ? (t('nav.master.dialogs.willCreate') || 'Will create:') : (t('nav.master.dialogs.willModify') || 'Will modify:')}
                        </p>
                        <p className="text-sm text-accent font-mono">
                            {getSummary()}
                        </p>
                    </div>
                )}

                <div className="px-6 py-4 border-t border-bd flex justify-end gap-3">
                    <button
                        type="button"
                        onClick={handleClose}
                        disabled={state.isSubmitting}
                        className="px-4 py-2 text-sm font-semibold text-secondary bg-surface-2 border border-bd rounded-lg hover:bg-surface transition-colors disabled:opacity-50"
                    >
                        {t('nav.master.dialogs.cancelCreate') || 'Cancel'}
                    </button>
                    <button
                        type="button"
                        onClick={handleSubmit}
                        disabled={state.isSubmitting}
                        className="px-4 py-2 text-sm font-semibold text-white bg-accent rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50"
                    >
                        {state.isSubmitting ? 'Processing...' : buttonText}
                    </button>
                </div>
            </div>
        </div>
    );
};
