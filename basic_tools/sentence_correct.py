import operator
import torch
from transformers import BertTokenizer, BertForMaskedLM
import numpy as np
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class SentenceCorrector:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("/Users/mirli/worker/code/code_work/model/macbert/")
        self.model = BertForMaskedLM.from_pretrained("/Users/mirli/worker/code/code_work/model/macbert/")
        self.model.to(device)
        self.special_token = ["¶", ",", ".", "-", "|"]
#(Ⅰ|Ⅱ|Ⅲ
    # |ⅣⅤⅥⅦⅧⅨⅩⅪⅫ)

    def get_errors(self, corrected_text, origin_text):
        sub_details = []
        for i, ori_char in enumerate(origin_text):
            if ori_char in [' ', '“', '”', '‘', '’', '琊', '\n', '…', '—', '擤']:
                # add unk word
                corrected_text = corrected_text[:i] + ori_char + corrected_text[i:]
                continue
            if i >= len(corrected_text):
                continue
            if ori_char in self.special_token:
                continue
            if ori_char != corrected_text[i]:
                if ori_char.lower() == corrected_text[i]:
                    # pass english upper char
                    corrected_text = corrected_text[:i] + ori_char + corrected_text[i + 1:]
                    continue
                sub_details.append((ori_char, corrected_text[i], i, i + 1))
        sub_details = sorted(sub_details, key=operator.itemgetter(2))
        return corrected_text, sub_details

    def process_text(self, texts):
        with torch.no_grad():
            outputs = self.model(**self.tokenizer(texts, padding=True, return_tensors='pt').to(device))

        result = []
        for ids, text in zip(outputs.logits, texts):
            ids_np = np.array(ids.cpu())
            probabilities = np.exp(ids_np) / np.sum(np.exp(ids_np))
            max_id = torch.argmax(ids, dim=-1)
            _text = self.tokenizer.decode(max_id, skip_special_tokens=True).replace(' ', '')

            # max_id = max_id.cpu().numpy()
            # prob_list = []
            # for idx,prob in enumerate(max_id):
            #     if idx == 0 or idx == len(max_id)-1:
            #         continue
            #     prob_list.append(probabilities[idx][prob])

            corrected_text = _text[:len(text)]
            # corrected_text = _text
            # print(prob_list)
            # print(_text)
            # print(len(prob_list),len(_text))
            # assert len(prob_list) == len(_text)

            corrected_text, details = self.get_errors(corrected_text, text)
            #print(text, ' => ', corrected_text, details)
            result.append({
                "target": corrected_text,
                "details": details
            })
        return result

