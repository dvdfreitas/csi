<?php

namespace Database\Seeders;

use App\Models\Llm;
use Illuminate\Database\Seeder;

class LlmSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * Unlike every other seeder here, this one holds its data inline: the list is
     * ours, not extracted from ESS sources, so there is nothing to validate a
     * JSON file against.
     */
    public function run(): void
    {
        // parameters is the number in the model's own name, which is what every paper and
        // table cites. The real count from the Hugging Face API goes in meta.parameters_exact,
        // because it does not match: the "7B" is really 7,615,616,512 parameters.
        // The license fields are copied from each model card's own cardData, verbatim:
        // "other" is what Hugging Face says when there is no standard identifier, and the
        // link is the actual document. Nothing here is our reading of what a licence allows.
        $llms = [
            [
                'code' => 'Qwen/Qwen2.5-0.5B-Instruct',
                'name' => 'Qwen2.5 0.5B Instruct',
                'family' => 'Qwen2.5',
                'parameters' => 0.5,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 494032768, 'developer' => 'Alibaba Cloud', 'license' => 'apache-2.0', 'license_link' => 'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/main/LICENSE'],
            ],
            [
                'code' => 'Qwen/Qwen2.5-3B-Instruct',
                'name' => 'Qwen2.5 3B Instruct',
                'family' => 'Qwen2.5',
                'parameters' => 3,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 3085938688, 'developer' => 'Alibaba Cloud', 'license' => 'other', 'license_name' => 'qwen-research', 'license_link' => 'https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE'],
            ],
            [
                'code' => 'Qwen/Qwen2.5-7B-Instruct',
                'name' => 'Qwen2.5 7B Instruct',
                'family' => 'Qwen2.5',
                'parameters' => 7,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 7615616512, 'developer' => 'Alibaba Cloud', 'license' => 'apache-2.0', 'license_link' => 'https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/LICENSE'],
            ],
            [
                'code' => 'Qwen/Qwen2.5-32B-Instruct',
                'name' => 'Qwen2.5 32B Instruct',
                'family' => 'Qwen2.5',
                'parameters' => 32,
                'is_instruct' => true,
                'notes' => 'The largest that fits on one H100 in bf16 (66 GB), and this cluster caps a user at 2 GPUs.',
                'meta' => ['parameters_exact' => 32763876352, 'developer' => 'Alibaba Cloud', 'license' => 'apache-2.0', 'license_link' => 'https://huggingface.co/Qwen/Qwen2.5-32B-Instruct/blob/main/LICENSE'],
            ],
            [
                'code' => 'Qwen/Qwen2.5-72B-Instruct',
                'name' => 'Qwen2.5 72B Instruct',
                'family' => 'Qwen2.5',
                'parameters' => 72,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 72706203648, 'developer' => 'Alibaba Cloud', 'license' => 'other', 'license_name' => 'qwen', 'license_link' => 'https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/blob/main/LICENSE'],
            ],
            [
                'code' => 'meta-llama/Llama-3.2-1B-Instruct',
                'name' => 'Llama 3.2 1B Instruct',
                'family' => 'Llama 3',
                'parameters' => 1,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 1235814400, 'developer' => 'Meta', 'license' => 'llama3.2', 'license_link' => 'https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct/blob/main/LICENSE.txt', 'gated' => 'manual'],
            ],
            [
                'code' => 'meta-llama/Llama-3.2-3B-Instruct',
                'name' => 'Llama 3.2 3B Instruct',
                'family' => 'Llama 3',
                'parameters' => 3,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 3212749824, 'developer' => 'Meta', 'license' => 'llama3.2', 'license_link' => 'https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/blob/main/LICENSE.txt', 'gated' => 'manual'],
            ],
            [
                'code' => 'meta-llama/Llama-3.1-8B-Instruct',
                'name' => 'Llama 3.1 8B Instruct',
                'family' => 'Llama 3',
                'parameters' => 8,
                'is_instruct' => true,
                'notes' => null,
                'meta' => ['parameters_exact' => 8030261248, 'developer' => 'Meta', 'license' => 'llama3.1', 'license_link' => 'https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/LICENSE', 'gated' => 'manual'],
            ],
            [
                'code' => 'meta-llama/Llama-3.3-70B-Instruct',
                'name' => 'Llama 3.3 70B Instruct',
                'family' => 'Llama 3',
                'parameters' => 70,
                'is_instruct' => true,
                'notes' => 'Needs 2 H100 in bf16 (141 GB), the same as the Qwen 72B — this cluster caps a user at 2 GPUs.',
                'meta' => ['parameters_exact' => 70553706496, 'developer' => 'Meta', 'license' => 'llama3.3', 'license_link' => 'https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct/blob/main/LICENSE', 'gated' => 'manual'],
            ],
        ];

        foreach ($llms as $llm) {
            Llm::updateOrCreate(['code' => $llm['code']], $llm);
        }

        $this->command->line('Imported '.count($llms).' LLMs.');
    }
}
