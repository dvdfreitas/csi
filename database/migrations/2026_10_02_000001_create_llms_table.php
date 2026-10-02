<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('llms', function (Blueprint $table) {
            $table->id();

            $table->string('code')->unique(); // Qwen/Qwen2.5-0.5B-Instruct (the Hugging Face id)
            $table->string('name'); // Qwen2.5 0.5B Instruct
            $table->string('family')->nullable()->index(); // Qwen2.5
            $table->decimal('parameters', 6, 2)->nullable(); // 0.5, 7, 70 — billions of parameters
            $table->boolean('is_instruct')->default(true); // false for base models, which have no chat template
            $table->text('notes')->nullable();
            $table->json('meta')->nullable(); // Anything not worth its own column yet: developer, licence, context window, release date

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('llms');
    }
};
