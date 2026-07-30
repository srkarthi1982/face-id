import { useState, useEffect } from 'react';
import { useI18n } from '../../locales/I18nContext';
import type { LocationType, UnitType, LocationChainItem, UnitChainItem } from '../../../modules/master/types';

const LOCATION_TYPES: LocationType[] = ['emirate', 'base', 'location', 'building', 'area'];
const UNIT_TYPES: UnitType[] = ['force', 'command', 'battalion', 'unit'];

const LOCATION_TYPE_LABELS: Record<LocationType, string> = {
    emirate: 'Emirate',
    base: 'Base',
    location: 'Location',
    building: 'Building',
    area: 'Area',
};

const UNIT_TYPE_LABELS: Record<UnitType, string> = {
    force: 'Force',
    command: 'Command',
    battalion: 'Battalion',
    unit: 'Unit',
};

export interface ChainStep {
    level: number;
    type: LocationType | UnitType;
    name: string;
    code?: string;
    skip: boolean;
}

interface CreateChainDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (chain: ChainStep[]) => Promise<void>;
    entityType: 'location' | 'unit';
}

export const CreateChainDialog: React.FC<CreateChainDialogProps> = ({
    isOpen,
    onClose,
    onSubmit,
    entityType
}) => {
    const { t } = useI18n();
    const [steps, setSteps] = useState<ChainStep[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const maxLevels = entityType === 'location' ? 5 : 4;
    const types = entityType === 'location' ? LOCATION_TYPES : UNIT_TYPES;
    const typeLabels = entityType === 'location' ? LOCATION_TYPE_LABELS : UNIT_TYPE_LABELS;

    useEffect(() => {
        if (isOpen) {
            const initialSteps: ChainStep[] = Array.from({ length: maxLevels }, (_, i) => ({
                level: i + 1,
                type: types[i],
                name: '',
                code: entityType === 'unit' ? '' : undefined,
                skip: i >= 2,
            }));
            setSteps(initialSteps);
            setError(null);
        }
    }, [isOpen, entityType, maxLevels, types]);

    const handleTypeChange = (index: number, type: LocationType | UnitType) => {
        setSteps(prev => prev.map((step, i) => 
            i === index ? { ...step, type } : step
        ));
    };

    const handleNameChange = (index: number, name: string) => {
        setSteps(prev => prev.map((step, i) => 
            i === index ? { ...step, name } : step
        ));
    };

    const handleCodeChange = (index: number, code: string) => {
        setSteps(prev => prev.map((step, i) => 
            i === index ? { ...step, code } : step
        ));
    };

    const handleSkipChange = (index: number, skip: boolean) => {
        setSteps(prev => prev.map((step, i) => {
            if (i !== index) return step;
            if (i < 2 && entityType === 'location') return step;
            return { ...step, skip };
        }));
    };

    const handleSubmit = async () => {
        const nonSkippedSteps = steps.filter(s => !s.skip);
        
        if (nonSkippedSteps.length === 0) {
            setError('At least one level must be created');
            return;
        }

        if (nonSkippedSteps.some(s => !s.name.trim())) {
            setError('All non-skipped levels must have a name');
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            await onSubmit(nonSkippedSteps);
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create chain');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-surface rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-border-bd">
                    <h2 className="text-xl font-semibold text-text-primary">
                        {entityType === 'location' 
                            ? t('nav.master.dialogs.createChain') || 'Create Location Chain'
                            : t('nav.master.dialogs.createChain') || 'Create Unit Chain'
                        }
                    </h2>
                    <p className="text-sm text-text-secondary mt-1">
                        {entityType === 'location'
                            ? 'Create multiple hierarchy levels at once. Emirates and Base are mandatory.'
                            : 'Create multiple hierarchy levels at once in strict order.'
                        }
                    </p>
                </div>

                <div className="p-6 space-y-4">
                    {steps.map((step, index) => {
                        const isMandatory = entityType === 'location' && index < 2;
                        const canSkip = !isMandatory;

                        return (
                            <div 
                                key={step.level}
                                className={`p-4 border rounded-lg transition-all ${
                                    step.skip 
                                        ? 'bg-gray-50 border-gray-200 opacity-60' 
                                        : 'bg-white border-border-bd'
                                }`}
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <span className="text-sm font-semibold text-text-primary min-w-[80px]">
                                        Level {step.level}
                                    </span>
                                    
                                    {canSkip && (
                                        <label className="flex items-center gap-2 text-sm">
                                            <input
                                                type="checkbox"
                                                checked={step.skip}
                                                onChange={(e) => handleSkipChange(index, e.target.checked)}
                                                className="rounded border-gray-300"
                                            />
                                            <span className="text-text-secondary">
                                                {t('nav.master.dialogs.skip') || 'Skip'}
                                            </span>
                                        </label>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-sm font-medium text-text-secondary mb-1">
                                            Type
                                        </label>
                                        <select
                                            value={step.type}
                                            onChange={(e) => handleTypeChange(index, e.target.value as LocationType | UnitType)}
                                            disabled={step.skip}
                                            className="w-full px-3 py-2 border border-border-bd rounded-md text-sm bg-surface focus:outline-none focus:border-accent"
                                        >
                                            {types.map(type => (
                                                <option key={type} value={type}>
                                                    {typeLabels[type as keyof typeof typeLabels]}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-text-secondary mb-1">
                                            Name *
                                        </label>
                                        <input
                                            type="text"
                                            value={step.name}
                                            onChange={(e) => handleNameChange(index, e.target.value)}
                                            disabled={step.skip}
                                            placeholder={`Enter ${typeLabels[step.type as keyof typeof typeLabels]} name`}
                                            className="w-full px-3 py-2 border border-border-bd rounded-md text-sm bg-surface focus:outline-none focus:border-accent"
                                        />
                                    </div>
                                </div>

                                {entityType === 'unit' && (
                                    <div className="mt-3">
                                        <label className="block text-sm font-medium text-text-secondary mb-1">
                                            Code (optional)
                                        </label>
                                        <input
                                            type="text"
                                            value={step.code || ''}
                                            onChange={(e) => handleCodeChange(index, e.target.value)}
                                            disabled={step.skip}
                                            placeholder={`Enter ${typeLabels[step.type as keyof typeof typeLabels]} code`}
                                            className="w-full px-3 py-2 border border-border-bd rounded-md text-sm bg-surface focus:outline-none focus:border-accent"
                                        />
                                    </div>
                                )}
                            </div>
                        );
                    })}

                    {error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-border-bd flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        disabled={isSubmitting}
                        className="px-4 py-2 text-sm font-medium text-text-secondary bg-surface border border-border-bd rounded-md hover:bg-gray-50 disabled:opacity-50"
                    >
                        {t('nav.master.dialogs.cancelCreate') || 'Cancel'}
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className="px-4 py-2 text-sm font-medium text-white bg-accent rounded-md hover:bg-accent/90 disabled:opacity-50"
                    >
                        {isSubmitting ? 'Creating...' : (t('nav.master.dialogs.confirmCreate') || 'Create Chain')}
                    </button>
                </div>
            </div>
        </div>
    );
};
