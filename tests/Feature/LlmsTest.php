<?php

use Database\Seeders\LlmSeeder;

test('llms page lists the seeded models', function () {
    $this->seed(LlmSeeder::class);

    $this->get(route('llms'))
        ->assertOk()
        ->assertSee('Qwen2.5 7B Instruct')
        ->assertSee('Qwen/Qwen2.5-7B-Instruct')
        ->assertSee('Alibaba Cloud')
        ->assertSee('Llama 3.3 70B Instruct')
        ->assertSee('llama3.3');
});
