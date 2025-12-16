<script lang="ts" setup>
import type { ToasterProps } from "vue-sonner"
import { reactiveOmit } from "@vueuse/core"
import { CircleCheckIcon, InfoIcon, Loader2Icon, OctagonXIcon, TriangleAlertIcon, XIcon } from "lucide-vue-next"
import { Toaster as Sonner } from "vue-sonner"

const props = defineProps<ToasterProps>()
const delegatedProps = reactiveOmit(props, "toastOptions")
</script>

<template>
  <Sonner
    class="toaster group"
    position="bottom-right"
    :toast-options="{
      classes: {
        toast: 'group toast group-[.toaster]:bg-vscode-bg-tertiary group-[.toaster]:text-vscode-text-primary group-[.toaster]:border group-[.toaster]:border-vscode-border-default group-[.toaster]:rounded-md group-[.toaster]:shadow-card-hover',
        description: 'group-[.toast]:text-vscode-text-secondary',
        actionButton:
          'group-[.toast]:bg-vscode-accent-primary group-[.toast]:text-vscode-text-primary group-[.toast]:hover:bg-vscode-accent-primary-hover',
        cancelButton:
          'group-[.toast]:bg-vscode-bg-elevated group-[.toast]:text-vscode-text-secondary',
        success: 'group-[.toaster]:!bg-vscode-accent-success group-[.toaster]:!text-white group-[.toaster]:border-vscode-accent-success',
        error: 'group-[.toaster]:!bg-vscode-accent-error group-[.toaster]:!text-white group-[.toaster]:border-vscode-accent-error',
        info: 'group-[.toaster]:!bg-vscode-accent-primary group-[.toaster]:!text-white group-[.toaster]:border-vscode-accent-primary',
      },
    }"
    v-bind="delegatedProps"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-4" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-4" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-4" />
    </template>
  </Sonner>
</template>
