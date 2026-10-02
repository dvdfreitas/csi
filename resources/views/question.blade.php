<x-layouts::app :title="__('Question')">
    <flux:breadcrumbs>
        <flux:breadcrumbs.item :href="route('questions')" wire:navigate>{{ __('Questions') }}</flux:breadcrumbs.item>
        <flux:breadcrumbs.item>#{{ $question->id }}</flux:breadcrumbs.item>
    </flux:breadcrumbs>

    <div class="mt-6 grid max-w-3xl gap-6">
        <flux:card>
            <flux:heading>{{ __('Statement') }}</flux:heading>
            <flux:text class="mt-2 whitespace-pre-wrap">{{ $question->statement }}</flux:text>
        </flux:card>

        <flux:card>
            <flux:heading>{{ __('Answer') }}</flux:heading>
            <flux:text class="mt-2 text-lg font-semibold">{{ $question->answer }}</flux:text>
        </flux:card>

        @if ($question->reasoning)
            <flux:card>
                <flux:heading>{{ __('Reasoning') }}</flux:heading>
                <flux:text class="mt-2 whitespace-pre-wrap">{{ $question->reasoning }}</flux:text>
            </flux:card>
        @endif

        <flux:card>
            <flux:heading>{{ __('Source') }}</flux:heading>
            <dl class="mt-2 grid grid-cols-[auto_1fr] gap-x-6 gap-y-1 text-sm">
                @foreach (['Dataset' => $question->dataset, 'Subdataset' => $question->subdataset, 'Split' => $question->split, 'Type' => $question->type, 'Language' => $question->language, 'Hash' => $question->hash] as $label => $value)
                    <dt class="text-zinc-500 dark:text-zinc-400">{{ __($label) }}</dt>
                    <dd class="font-mono text-zinc-800 dark:text-zinc-200">{{ $value }}</dd>
                @endforeach
            </dl>
        </flux:card>
    </div>
</x-layouts::app>
