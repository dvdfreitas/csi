<section class="w-full">
    <flux:heading size="xl" level="1">{{ __('Questions') }}</flux:heading>

    <flux:table :paginate="$questions" class="mt-6">
        <flux:table.columns>
            <flux:table.column>{{ __('Dataset') }}</flux:table.column>
            <flux:table.column>{{ __('Split') }}</flux:table.column>
            <flux:table.column>{{ __('Statement') }}</flux:table.column>
            <flux:table.column>{{ __('Answer') }}</flux:table.column>
            <flux:table.column>{{ __('Type') }}</flux:table.column>
            <flux:table.column>{{ __('Language') }}</flux:table.column>
        </flux:table.columns>

        <flux:table.rows>
            @foreach ($questions as $question)
                <flux:table.row :key="$question->id">
                    <flux:table.cell>{{ $question->dataset }}/{{ $question->subdataset }}</flux:table.cell>
                    <flux:table.cell>{{ $question->split }}</flux:table.cell>
                    <flux:table.cell class="whitespace-normal">
                        <flux:link :href="route('questions.show', $question->id)" wire:navigate>{{ Str::limit($question->statement, 120) }}</flux:link>
                    </flux:table.cell>
                    <flux:table.cell variant="strong">{{ $question->answer }}</flux:table.cell>
                    <flux:table.cell>{{ $question->type }}</flux:table.cell>
                    <flux:table.cell>{{ $question->language }}</flux:table.cell>
                </flux:table.row>
            @endforeach
        </flux:table.rows>
    </flux:table>
</section>
