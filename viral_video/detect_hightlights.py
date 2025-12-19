import re
from sentence_transformers import SentenceTransformer, util
import torch

def read_transcript(path):
    with open(path, "r") as f:
        text = f.read()
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def rank_sentences(sentences):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    excitement_prompt = "exciting, emotional, shocking, funny, surprising moment"

    anchor_emb = model.encode(excitement_prompt, convert_to_tensor=True)
    sentence_embs = model.encode(sentences, convert_to_tensor=True)
    scores = util.cos_sim(anchor_emb, sentence_embs)[0]

    top_k = torch.topk(scores, k=min(10, len(sentences)))
    highlights = [(sentences[i], float(scores[i])) for i in top_k.indices]
    return highlights

def save_highlight_timestamps(highlights, output_file="highlights.txt"):
    pattern = re.compile(r"\[(\d+\.\d+) - (\d+\.\d+)\]")
    with open(output_file, "w") as f:
        for sent, score in highlights:
            match = pattern.search(sent)
            if match:
                start, end = match.groups()
                f.write(f"[{start} - {end}]  ({score:.3f})  {sent}\n")

if __name__ == "__main__":
    transcript_path = "transcript.txt"
    sentences = read_transcript(transcript_path)
    highlights = rank_sentences(sentences)

    print("\n🔥 Top potential highlight moments:\n")
    for i, (sent, score) in enumerate(highlights, 1):
        print(f"{i}. ({score:.3f}) {sent}")

    # Save timestamps for trimmer
    save_highlight_timestamps(highlights)
    print("\n💾 Saved filtered highlight timestamps → highlights.txt")
