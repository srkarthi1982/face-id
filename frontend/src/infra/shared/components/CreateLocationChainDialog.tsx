import { useState, useEffect, useCallback } from 'react';
import { useI18n } from '../../locales/I18nContext';
import { SearchableCombobox, type SelectOption } from './SearchableCombobox';
import type { LocationType } from '../../../modules/master/types';
import { HiOutlineXMark } from 'react-icons/hi2';

interface LocationItem {
    id: number;
    name: string;
    parent_id?: number | null;
    unit_id?: number | null;
}

interface LocationLevel {
    id: number | null;
    name: string;
    isCreating: boolean;
}

interface CreateLocationChainDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (chain: { 
        chain: Array<{ 
            type: LocationType; 
            id?: number; 
            name: string;
            unit_id?: number | null;
        }> 
    }) => Promise<void>;
    existingEmirates: LocationItem[];
    existingBases: LocationItem[];
    existingLocations: LocationItem[];
    existingBuildings: LocationItem[];
    existingAreas: LocationItem[];
    closeOnBackdropClick?: boolean;
}

interface DialogState {
    emirate: LocationLevel;
    base: LocationLevel;
    location: LocationLevel;
    building: LocationLevel;
    area: LocationLevel;
    hasUnsavedChanges: boolean;
    isSubmitting: boolean;
    error: string | null;
}

const EMPTY_LEVEL: LocationLevel = {
    id: null,
    name: '',
    isCreating: false,
};

export const CreateLocationChainDialog: React.FC<CreateLocationChainDialogProps> = ({
    isOpen,
    onClose,
    onSubmit,
    existingEmirates,
    existingBases,
    existingLocations,
    existingBuildings,
    existingAreas,
    closeOnBackdropClick = false,
}) => {
    const { t } = useI18n();
    
    const [state, setState] = useState<DialogState>({
        emirate: { ...EMPTY_LEVEL },
        base: { ...EMPTY_LEVEL },
        location: { ...EMPTY_LEVEL },
        building: { ...EMPTY_LEVEL },
        area: { ...EMPTY_LEVEL },
        hasUnsavedChanges: false,
        isSubmitting: false,
        error: null,
    });

    const showBase = state.emirate.id !== null || state.emirate.isCreating;
    const showLocation = state.base.id !== null || state.base.isCreating;
    const showBuilding = showLocation;
    const showArea = showLocation;

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
            emirate: { ...EMPTY_LEVEL },
            base: { ...EMPTY_LEVEL },
            location: { ...EMPTY_LEVEL },
            building: { ...EMPTY_LEVEL },
            area: { ...EMPTY_LEVEL },
            error: null,
        }));
        onClose();
    }, [state.hasUnsavedChanges, onClose, t]);

    const updateLevel = useCallback(<K extends 'emirate' | 'base' | 'location' | 'building' | 'area'>(
        level: K,
        updates: Partial<LocationLevel>
    ) => {
        setState(prev => ({
            ...prev,
            [level]: { ...prev[level], ...updates },
        }));
    }, []);

    const handleEmirateSelect = useCallback((selected: { id: number; name: string } | null) => {
        if (selected) {
            updateLevel('emirate', { id: selected.id, name: selected.name, isCreating: false });
        } else {
            updateLevel('emirate', { id: null, name: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleEmirateCreate = useCallback((name: string) => {
        updateLevel('emirate', { name, isCreating: true, id: null });
    }, [updateLevel]);

    const handleBaseSelect = useCallback((selected: { id: number; name: string } | null) => {
        if (selected) {
            updateLevel('base', { id: selected.id, name: selected.name, isCreating: false });
        } else {
            updateLevel('base', { id: null, name: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleBaseCreate = useCallback((name: string) => {
        updateLevel('base', { name, isCreating: true, id: null });
    }, [updateLevel]);

    const handleLocationSelect = useCallback((selected: { id: number; name: string } | null) => {
        if (selected) {
            updateLevel('location', { id: selected.id, name: selected.name, isCreating: false });
        } else {
            updateLevel('location', { id: null, name: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleLocationCreate = useCallback((name: string) => {
        updateLevel('location', { name, isCreating: true, id: null });
    }, [updateLevel]);

    const handleBuildingSelect = useCallback((selected: { id: number; name: string } | null) => {
        if (selected) {
            updateLevel('building', { id: selected.id, name: selected.name, isCreating: false });
        } else {
            updateLevel('building', { id: null, name: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleBuildingCreate = useCallback((name: string) => {
        updateLevel('building', { name, isCreating: true, id: null });
    }, [updateLevel]);

    const handleAreaSelect = useCallback((selected: { id: number; name: string } | null) => {
        if (selected) {
            updateLevel('area', { id: selected.id, name: selected.name, isCreating: false });
        } else {
            updateLevel('area', { id: null, name: '', isCreating: false });
        }
    }, [updateLevel]);

    const handleAreaCreate = useCallback((name: string) => {
        updateLevel('area', { name, isCreating: true, id: null });
    }, [updateLevel]);

    const validate = (): boolean => {
        const errors: string[] = [];
        
        // Emirate is always required
        if (state.emirate.id === null && !state.emirate.isCreating) {
            errors.push('Emirate is required');
        }
        
        // Base is required only if user has entered a name (creating beyond Emirate level)
        if (showBase && state.base.name.trim() !== '' && state.base.id === null && !state.base.isCreating) {
            errors.push('Base is required');
        }
        
        // Location is optional - only validate if name is filled
        if (showLocation && state.location.name.trim() !== '') {
            if (state.location.id === null && !state.location.isCreating) {
                errors.push('Location is required');
            }
        }
        
        // Building is optional - only validate if name is filled
        if (showBuilding && state.building.name.trim() !== '') {
            if (state.building.id === null && !state.building.isCreating) {
                errors.push('Building is required');
            }
        }
        
        // Area is optional - only validate if name is filled
        if (showArea && state.area.name.trim() !== '') {
            if (state.area.id === null && !state.area.isCreating) {
                errors.push('Area is required');
            }
        }
        
        if (errors.length > 0) {
            setState(prev => ({ ...prev, error: errors.join(', ') }));
            return false;
        }
        
        return true;
    };

    const buildChain = () => {
        const chain: Array<{ type: LocationType; id?: number; name: string }> = [];
        
        if (state.emirate.isCreating) {
            chain.push({ type: 'emirate', name: state.emirate.name });
        } else if (state.emirate.id) {
            chain.push({ type: 'emirate', id: state.emirate.id, name: state.emirate.name });
        }
        
        // Only include Base if it's selected/created
        if (showBase) {
            if (state.base.isCreating) {
                chain.push({ type: 'base', name: state.base.name });
            } else if (state.base.id) {
                chain.push({ type: 'base', id: state.base.id, name: state.base.name });
            }
        }
        
        // Only include Location if name is filled
        if (showLocation && state.location.name.trim() !== '') {
            if (state.location.isCreating) {
                chain.push({ type: 'location', name: state.location.name });
            } else if (state.location.id) {
                chain.push({ type: 'location', id: state.location.id, name: state.location.name });
            }
        }
        
        // Only include Building if name is filled
        if (showBuilding && state.building.name.trim() !== '') {
            if (state.building.isCreating) {
                chain.push({ type: 'building', name: state.building.name });
            } else if (state.building.id) {
                chain.push({ type: 'building', id: state.building.id, name: state.building.name });
            }
        }
        
        // Only include Area if name is filled
        if (showArea && state.area.name.trim() !== '') {
            if (state.area.isCreating) {
                chain.push({ type: 'area', name: state.area.name });
            } else if (state.area.id) {
                chain.push({ type: 'area', id: state.area.id, name: state.area.name });
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
                emirate: { ...EMPTY_LEVEL },
                base: { ...EMPTY_LEVEL },
                location: { ...EMPTY_LEVEL },
                building: { ...EMPTY_LEVEL },
                area: { ...EMPTY_LEVEL },
                hasUnsavedChanges: false,
            }));
            onClose();
        } catch (err) {
            setState(prev => ({
                ...prev,
                error: err instanceof Error ? err.message : 'Failed to create locations',
            }));
        } finally {
            setState(prev => ({ ...prev, isSubmitting: false }));
        }
    };

    const getSummary = () => {
        const parts: string[] = [];
        
        if (state.emirate.id || state.emirate.isCreating) {
            parts.push(state.emirate.name || 'Emirate');
        }
        if (showBase && (state.base.id || state.base.isCreating)) {
            parts.push(state.base.name || 'Base');
        }
        // Only show Location if name is filled
        if (showLocation && state.location.name.trim() !== '' && (state.location.id || state.location.isCreating)) {
            parts.push(state.location.name);
        }
        // Only show Building if name is filled
        if (showBuilding && state.building.name.trim() !== '' && (state.building.id || state.building.isCreating)) {
            parts.push(state.building.name);
        }
        // Only show Area if name is filled
        if (showArea && state.area.name.trim() !== '' && (state.area.id || state.area.isCreating)) {
            parts.push(state.area.name);
        }
        
        return parts.join(' > ');
    };

    const hasNewItems = state.emirate.isCreating || state.base.isCreating || state.location.isCreating || state.building.isCreating || state.area.isCreating;
    const buttonText = hasNewItems 
        ? t('nav.master.dialogs.createLocations') || 'Create Locations'
        : t('nav.master.dialogs.modifyLocation') || 'Modify Location';

    if (!isOpen) return null;

    const emirateOptions: SelectOption[] = existingEmirates
        .map(e => ({ 
            id: e.id, 
            value: e.name,
            meta: { name: e.name, parent_id: e.parent_id }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    const baseOptions: SelectOption[] = existingBases
        .filter(b => state.emirate.id ? b.parent_id === state.emirate.id : true)
        .map(b => ({ 
            id: b.id, 
            value: b.name,
            meta: { name: b.name, parent_id: b.parent_id }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    const locationOptions: SelectOption[] = existingLocations
        .filter(l => state.base.id ? l.parent_id === state.base.id : true)
        .map(l => ({ 
            id: l.id, 
            value: l.name,
            meta: { name: l.name, parent_id: l.parent_id }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    const buildingOptions: SelectOption[] = existingBuildings
        .filter(b => state.location.id ? b.parent_id === state.location.id : true)
        .map(b => ({ 
            id: b.id, 
            value: b.name,
            meta: { name: b.name, parent_id: b.parent_id }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));
    
    const areaOptions: SelectOption[] = existingAreas
        .filter(a => state.building.id ? a.parent_id === state.building.id : true)
        .map(a => ({ 
            id: a.id, 
            value: a.name,
            meta: { name: a.name, parent_id: a.parent_id }
        }))
        .sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }));

    const nameInputClass = 'flex-1 px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20';

    const renderLevelRow = (
        label: string,
        level: LocationLevel,
        options: SelectOption[],
        onSelect: (selected: { id: number; name: string } | null) => void,
        onCreate: (name: string) => void,
        levelKey: 'emirate' | 'base' | 'location' | 'building' | 'area',
        useCombobox: boolean = true
    ) => (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-primary">{label} *</span>
                {level.isCreating && <span className="text-xs text-accent">Creating new</span>}
            </div>
            <div className="flex items-center gap-2">
                {useCombobox ? (
                    <SearchableCombobox
                        options={options}
                        placeholder="Type name or search..."
                        selected={level.id ? { id: level.id, value: level.name } : null}
                        onChange={(selected) => {
                            if (selected) {
                                onSelect({ id: selected.id as number, name: selected.value });
                            } else {
                                onSelect(null);
                            }
                        }}
                        onAddNew={onCreate}
                        className="w-64"
                    />
                ) : (
                    <input
                        type="text"
                        placeholder="Name *"
                        value={level.name}
                        onChange={(e) => {
                            updateLevel(levelKey, { name: e.target.value });
                            if (e.target.value && !level.isCreating && level.id === null) {
                                onCreate(e.target.value);
                            }
                        }}
                        className={nameInputClass}
                    />
                )}
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
                    <h2 className="text-xl font-semibold text-primary">{t('nav.master.dialogs.createLocation') || 'Create Location'}</h2>
                    <button
                        onClick={handleClose}
                        className="p-2 rounded-lg hover:bg-surface-2 transition-colors"
                        title="Close"
                    >
                        <HiOutlineXMark className="w-5 h-5 text-secondary" />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    {renderLevelRow(
                        'Emirate',
                        state.emirate,
                        emirateOptions,
                        handleEmirateSelect,
                        handleEmirateCreate,
                        'emirate'
                    )}

                    {showBase && renderLevelRow(
                        'Base',
                        state.base,
                        baseOptions,
                        handleBaseSelect,
                        handleBaseCreate,
                        'base'
                    )}

                    {showLocation && renderLevelRow(
                        'Location',
                        state.location,
                        locationOptions,
                        handleLocationSelect,
                        handleLocationCreate,
                        'location'
                    )}

                    {showBuilding && renderLevelRow(
                        'Building',
                        state.building,
                        buildingOptions,
                        handleBuildingSelect,
                        handleBuildingCreate,
                        'building'
                    )}

                    {showArea && renderLevelRow(
                        'Area',
                        state.area,
                        areaOptions,
                        handleAreaSelect,
                        handleAreaCreate,
                        'area',
                        false  // Area uses simple input, not combobox
                    )}

                    {state.error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-sm text-red-500">{state.error}</p>
                        </div>
                    )}
                </div>

                {(state.emirate.id || state.emirate.isCreating || state.base.id || state.base.isCreating || 
                  state.location.id || state.location.isCreating || state.building.id || state.building.isCreating || 
                  state.area.id || state.area.isCreating) && (
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
                        {t('common.cancel') || 'Cancel'}
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
