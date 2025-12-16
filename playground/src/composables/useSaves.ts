import { ref, computed } from 'vue'
import type { SavedConfiguration, SavesData } from '@/types/saves'

const STORAGE_KEY = 'shui-playground-saves'
const STORAGE_VERSION = '1.0.0'
const MAX_SAVES = 50

/**
 * Composable for managing saved configurations in localStorage
 */
export function useSaves() {
  const saves = ref<SavedConfiguration[]>([])
  const activeSaveId = ref<string | null>(null)

  // Load saves from localStorage
  const loadSaves = (): void => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data: SavesData = JSON.parse(stored)
        if (data.version === STORAGE_VERSION) {
          // Migrate old saves with focusNode/focusNodeDatatype strings to new FocusNode structure
          const migratedSaves = data.saves.map((save: any) => {
            if (typeof save.focusNode === 'string') {
              // Old format: separate focusNode and focusNodeDatatype
              const focusNodeDatatype = save.focusNodeDatatype
              const focusNodeValue = save.focusNode

              // Create new FocusNode object (literal with datatype)
              const newFocusNode = {
                type: 'LITERAL' as const,
                value: focusNodeValue,
                datatype: focusNodeDatatype,
              }

              // Remove old focusNodeDatatype field and replace focusNode
              const { focusNodeDatatype: _, ...rest } = save
              return {
                ...rest,
                focusNode: newFocusNode,
              }
            }
            return save
          })

          saves.value = migratedSaves.sort((a, b) => b.timestamp - a.timestamp)
        }
      }
    } catch (error) {
      console.error('Failed to load saves from localStorage:', error)
      saves.value = []
    }
  }

  // Save to localStorage
  const persistSaves = (): void => {
    try {
      const data: SavesData = {
        version: STORAGE_VERSION,
        saves: saves.value,
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
      throw new Error('Failed to save configuration. Storage may be full.')
    }
  }

  // Create a new save
  const createSave = (name: string, config: Omit<SavedConfiguration, 'id' | 'name' | 'timestamp'>): SavedConfiguration => {
    const save: SavedConfiguration = {
      id: `save-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      timestamp: Date.now(),
      ...config,
    }

    saves.value.unshift(save)

    // Enforce max saves limit
    if (saves.value.length > MAX_SAVES) {
      saves.value = saves.value.slice(0, MAX_SAVES)
    }

    persistSaves()
    return save
  }

  // Update an existing save
  const updateSave = (id: string, config: Omit<SavedConfiguration, 'id' | 'name' | 'timestamp'>): void => {
    const index = saves.value.findIndex((s) => s.id === id)
    if (index === -1) {
      throw new Error('Save not found')
    }

    saves.value[index] = {
      ...saves.value[index],
      ...config,
      timestamp: Date.now(),
    }

    // Re-sort by timestamp
    saves.value.sort((a, b) => b.timestamp - a.timestamp)
    persistSaves()
  }

  // Delete a save
  const deleteSave = (id: string): void => {
    saves.value = saves.value.filter((s) => s.id !== id)
    if (activeSaveId.value === id) {
      activeSaveId.value = null
    }
    persistSaves()
  }

  // Get a save by ID
  const getSave = (id: string): SavedConfiguration | undefined => {
    return saves.value.find((s) => s.id === id)
  }

  // Check if saves exist in localStorage
  const hasSaves = computed(() => saves.value.length > 0)

  // Check if a save name already exists
  const saveNameExists = (name: string, excludeId?: string): boolean => {
    return saves.value.some((s) => s.name === name && s.id !== excludeId)
  }

  // Initialize: load saves from localStorage
  loadSaves()

  return {
    saves,
    activeSaveId,
    hasSaves,
    loadSaves,
    createSave,
    updateSave,
    deleteSave,
    getSave,
    saveNameExists,
  }
}
