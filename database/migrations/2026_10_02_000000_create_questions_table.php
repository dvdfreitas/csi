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
        Schema::create('questions', function (Blueprint $table) {
            $table->id();

            $table->string('dataset');
            $table->string('subdataset')->default('default');
            $table->string('split');
            $table->char('hash', 64);

            $table->string('type');
            $table->string('language', 10);

            $table->text('statement');
            $table->text('answer');
            $table->text('reasoning')->nullable();

            $table->timestamps();

            $table->unique(['dataset', 'subdataset', 'split', 'hash']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('questions');
    }
};
