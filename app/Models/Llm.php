<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

/**
 * @property int $id
 * @property string $code
 * @property string $name
 * @property string|null $family
 * @property float|null $parameters
 * @property bool $is_instruct
 * @property string|null $notes
 * @property array<string, mixed>|null $meta
 * @property Carbon|null $created_at
 * @property Carbon|null $updated_at
 */
#[Fillable([
    'code',
    'name',
    'family',
    'parameters',
    'is_instruct',
    'notes',
    'meta',
])]
class Llm extends Model
{
    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            // Cast to float, not decimal: this column exists to be sorted and plotted.
            'parameters' => 'float',
            'is_instruct' => 'boolean',
            'meta' => 'array',
        ];
    }
}
