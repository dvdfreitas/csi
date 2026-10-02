<?php

use App\Livewire\Questions;
use Illuminate\Support\Facades\DB;
use Livewire\Livewire;

function question(int $i): array
{
    return [
        'dataset' => 'openai/gsm8k',
        'subdataset' => 'main',
        'split' => 'test',
        'hash' => str_pad((string) $i, 64, '0', STR_PAD_LEFT),
        'type' => 'numeric',
        'language' => 'en',
        'statement' => "Pergunta {$i}",
        'answer' => (string) $i,
    ];
}

test('questions page is visible without logging in', function () {
    DB::table('questions')->insert(question(1));

    $this->get(route('questions'))
        ->assertOk()
        ->assertSee('openai/gsm8k/main')
        ->assertSee('Pergunta 1');
});

test('questions page paginates', function () {
    DB::table('questions')->insert(collect(range(1, 26))->map(question(...))->all());

    Livewire::test(Questions::class)
        ->assertSee('Pergunta 25')
        ->assertDontSee('Pergunta 26')
        ->call('nextPage')
        ->assertSee('Pergunta 26')
        ->assertDontSee('Pergunta 25');
});

test('a question page shows the answer and the reasoning', function () {
    DB::table('questions')->insert([...question(1), 'reasoning' => 'Primeiro isto.
Depois aquilo.']);
    $id = DB::table('questions')->value('id');

    $this->get(route('questions.show', $id))
        ->assertOk()
        ->assertSee('Pergunta 1')
        ->assertSee('Primeiro isto.')
        ->assertSee('openai/gsm8k');
});

test('an unknown question is a 404', function () {
    $this->get(route('questions.show', 123))->assertNotFound();
});
