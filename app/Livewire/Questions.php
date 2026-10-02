<?php

namespace App\Livewire;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;
use Livewire\Attributes\Title;
use Livewire\Component;
use Livewire\WithPagination;

#[Title('Questions')]
class Questions extends Component
{
    use WithPagination;

    public function render(): View
    {
        return view('livewire.questions', [
            'questions' => DB::table('questions')->orderBy('id')->paginate(25),
        ]);
    }
}
