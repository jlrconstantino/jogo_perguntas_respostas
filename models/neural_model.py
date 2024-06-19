import torch
from transformers import BertForQuestionAnswering, BertTokenizerFast

model_path = "./models/Bert_FaQuAD_20ep"
neural_model = BertForQuestionAnswering.from_pretrained(model_path)
tokenizer = BertTokenizerFast.from_pretrained(model_path)

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f'Working on {device}')

neural_model = neural_model.to(device)

def get_prediction(context, question):
  inputs = tokenizer.encode_plus(question, context, return_tensors='pt').to(device)
  outputs = neural_model(**inputs)

  answer_start = torch.argmax(outputs[0])
  answer_end = torch.argmax(outputs[1]) + 1

  answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][answer_start:answer_end]))

  return answer