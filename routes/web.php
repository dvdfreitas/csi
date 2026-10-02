<?php

use App\Livewire\Questions;
use App\Models\Llm;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;

Route::view('/', 'welcome')->name('home');

Route::get('llms', fn () => view('llms', [
    'llms' => Llm::orderBy('parameters')->get(),
]))->name('llms');

Route::livewire('questions', Questions::class)->name('questions');

Route::get('questions/{id}', function (int $id) {
    abort_if(($question = DB::table('questions')->find($id)) === null, 404);

    return view('question', ['question' => $question]);
})->name('questions.show');

Route::middleware(['auth', 'verified'])->group(function () {
    Route::view('dashboard', 'dashboard')->name('dashboard');
});

require __DIR__.'/settings.php';
