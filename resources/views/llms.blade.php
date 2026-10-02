<x-layouts::app :title="__('LLMs')">
    <flux:heading size="xl" level="1">{{ __('LLMs') }}</flux:heading>

    <flux:table class="mt-6">
        <flux:table.columns>
            <flux:table.column>{{ __('Name') }}</flux:table.column>
            <flux:table.column>{{ __('Family') }}</flux:table.column>
            <flux:table.column class="text-end">{{ __('Params (B)') }}</flux:table.column>
            <flux:table.column>{{ __('Developer') }}</flux:table.column>
            <flux:table.column>{{ __('License') }}</flux:table.column>
            <flux:table.column>{{ __('Code') }}</flux:table.column>
        </flux:table.columns>

        <flux:table.rows>
            @foreach ($llms as $llm)
                <flux:table.row :key="$llm->id">
                    <flux:table.cell variant="strong">{{ $llm->name }}</flux:table.cell>
                    <flux:table.cell>{{ $llm->family }}</flux:table.cell>
                    <flux:table.cell class="text-end">{{ $llm->parameters }}</flux:table.cell>
                    <flux:table.cell>{{ $llm->meta['developer'] ?? '' }}</flux:table.cell>
                    <flux:table.cell>{{ $llm->meta['license'] ?? '' }}</flux:table.cell>
                    <flux:table.cell class="font-mono text-xs">{{ $llm->code }}</flux:table.cell>
                </flux:table.row>
            @endforeach
        </flux:table.rows>
    </flux:table>
</x-layouts::app>
