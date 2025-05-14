# Step 1: For generating the HTML from the designs / sketches with LLMs
python -m src.experiments.ollama_sketch \
--model llama3.2-vision --input_dir src/datasets/sketch 

python -m src.experiments.ollama_sketch \
--model llama3.2-vision --input_dir src/datasets/sketch --endpoint http://localhost:8888

python -m src.experiments.azure_sketch \
--model gpt-4o --input_dir src/datasets/sketch \
--endpoint <AZURE ENDPOINT> \
--api_key <AZURE API KEY>

python -m src.experiments.openai_sketch \
--model grok-2-vision --input_dir src/datasets/sketch \
--endpoint https://api.x.ai/v1 \
--api_key <OPENAI API KEY>

python -m src.experiments.gemini_sketch \
--model gemini-2.0-flash --input_dir src/datasets/sketch \
--api_key <GEMINI API KEY>

python -m src.experiments.replicate_sketch \
--model deepseek-ai/deepseek-vl2:e5caf557dd9e5dcee46442e1315291ef1867f027991ede8ff95e304d4f734200 \
--input_dir src/datasets/sketch \
--api_key <REPLICATE API KEY>

# Step 2: For evaluating the generated HTML 
python -m src.experiments.eval_responsive \
--original_dir ./src/datasets/sketch \
--generated_dir ./src/experiment-results/ollama_llama3.2-vision_20250315-025136/
