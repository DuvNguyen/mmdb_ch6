"""
searcher.py
===========
Chua 2 ham Find:
  - Find(Word, Weight, N)
  - Find(WordFile, N)

LY THUYET - Tim kiem voi Inverted Index:
-----------------------------------------
Khi co TermTable roi, tim kiem rat nhanh:
  - Thay vi doc toan bo M x N entries, ta chi xem
    dung list cac doc chua tu can tim.

SCORING (tinh diem):
  Moi document duoc gan mot SCORE the hien muc do lien quan.
  Score cang cao = document cang phu hop voi query.

  Cong thuc (tu frequency table trong slide):
    score(doc) = sum(  freq(term, doc) * weight(term)  )

  Trong do:
    freq(term, doc) = so lan term xuat hien trong doc
                    = TermTable[term][doc_id]
    weight(term)    = do quan trong cua term trong query
                    (nguoi dung tu xac dinh)

  Day chinh la DOT PRODUCT giua:
    - vecQ   : vector query   [w1, w2, ..., wM]
    - FreqT  : cot cua doc trong frequency table

  => Giong het cong thuc cosine/term distance trong slide!

Vi du:
  Query: cartel (weight=2), connections (weight=1)
  Doc1:  cartel xuat hien 3 lan, connections xuat hien 1 lan
  Score(Doc1) = 3*2 + 1*1 = 7
"""

import heapq   # dung de lay top-N hieu qua
import os


def Find(Word: str, Weight: int, N: int,
         DocTable: dict, TermTable: dict) -> list:
    """
    Tim top N documents lien quan den mot tu don.

    Tham so:
        Word      : tu can tim (string)
        Weight    : do quan trong cua tu nay trong query
        N         : so luong ket qua tra ve
        DocTable  : { doc_id -> ten_file }
        TermTable : { tu -> { doc_id: so_lan } }

    Tra ve:
        List cac tuple (score, ten_file) sap xep giam dan theo score
        Chi tra ve toi da N ket qua

    LY THUYET:
        score(doc) = freq(Word, doc) * Weight
        Chi xem cac doc co chua Word (bo qua doc co freq=0)
    """
    word = Word.lower()
    print(f"\n[Searcher] Find('{word}', weight={Weight}, top={N})")

    # Kiem tra tu co trong index khong
    if word not in TermTable:
        print(f"[Searcher] Tu '{word}' khong co trong TermTable.")
        return []

    # Tinh score cho tung doc chua tu nay
    scores = {}
    for doc_id, freq in TermTable[word].items():
        scores[doc_id] = freq * Weight

    # Lay top N theo score (dung heapq.nlargest de hieu qua)
    top_n = heapq.nlargest(N, scores.items(), key=lambda x: x[1])

    # Dinh dang ket qua: (score, ten_file)
    results = [(score, DocTable[doc_id]) for doc_id, score in top_n]

    _print_results(results)
    return results


def FindWordFile(WordFile: str, N: int,
                 DocTable: dict, TermTable: dict) -> list:
    """
    Tim top N documents dua tren nhieu tu co trong WordFile.

    Tham so:
        WordFile  : duong dan den file chua cac cap (tu, weight)
                    Moi dong: "ten_tu   so_nguyen"
                    Vi du:
                        cartel 2
                        connections 1
                        criminal 1
        N         : so luong ket qua tra ve
        DocTable  : { doc_id -> ten_file }
        TermTable : { tu -> { doc_id: so_lan } }

    Tra ve:
        List cac tuple (score, ten_file) sap xep giam dan theo score

    LY THUYET - Multi-word query:
        score(doc) = SUM[ freq(term_i, doc) * weight_i ]
                   = vecQ · FreqT_col(doc)

        Day la DOT PRODUCT trong slide (Closeness metric)!
        Cang nhieu tu query xuat hien nhieu trong doc,
        score cang cao, doc cang lien quan.
    """
    print(f"\n[Searcher] FindWordFile('{WordFile}', top={N})")

    # Doc WordFile: moi dong la "tu  weight"
    query_terms = _parse_word_file(WordFile)
    if not query_terms:
        print("[Searcher] WordFile trong hoac khong doc duoc.")
        return []

    print(f"[Searcher] Query terms: {query_terms}")

    # Tinh tong score cho tung doc
    scores = {}
    for word, weight in query_terms.items():
        if word not in TermTable:
            print(f"[Searcher]   '{word}' khong co trong index, bo qua.")
            continue

        for doc_id, freq in TermTable[word].items():
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += freq * weight
            # Vi du: cartel xuat hien 2 lan, weight=2 -> cong them 4

    if not scores:
        print("[Searcher] Khong tim thay document nao.")
        return []

    # Lay top N
    top_n = heapq.nlargest(N, scores.items(), key=lambda x: x[1])
    results = [(score, DocTable[doc_id]) for doc_id, score in top_n]

    _print_results(results)
    return results


# ------------------------------------------------------------------
# Ham ho tro (private)
# ------------------------------------------------------------------

def _parse_word_file(filepath: str) -> dict:
    """
    Doc WordFile, tra ve dict { tu: weight }.

    Dinh dang moi dong: "tu  weight"
    Bo qua dong trong hoac dong bat dau bang '#' (comment).
    """
    query = {}
    if not os.path.exists(filepath):
        print(f"[Searcher] Loi: Khong tim thay file '{filepath}'")
        return query

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                word   = parts[0].lower()
                try:
                    weight = int(parts[1])
                    query[word] = weight
                except ValueError:
                    print(f"[Searcher] Bo qua dong loi dinh dang: '{line}'")
    return query


def _print_results(results: list):
    """In ket qua tim kiem dep."""
    if not results:
        print("[Searcher] Khong co ket qua.")
        return
    print(f"[Searcher] Top {len(results)} ket qua:")
    for rank, (score, filename) in enumerate(results, 1):
        print(f"  #{rank}  {filename:<20}  score = {score}")
