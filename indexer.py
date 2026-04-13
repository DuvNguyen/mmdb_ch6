"""
indexer.py
==========
Chua ham CreateIndex(Dir, StopList)

LY THUYET - Inverted Index:
---------------------------
Inverted Index la cau truc du lieu nguoc: thay vi hoi
  "document nay chua nhung tu gi?"  (forward index)
ta xay:
  "tu nay xuat hien trong nhung doc nao?"  (inverted index)

Gom 2 bang:
  DocTable  : { doc_id -> ten_file }
              Vi du: { 0: "doc1.txt", 1: "doc2.txt" }

  TermTable : { tu -> { doc_id: so_lan_xuat_hien } }
              Vi du: { "cartel": {0: 1, 1: 2}, "crime": {0: 1} }

Dieu kien dac biet cua bai nay:
  TermTable chi chua cac tu BAT DAU BANG CHU 'C' (hoa hoac thuong)
  => Day la rang buoc de thu index nho gon hon

Quy trinh CreateIndex:
  1. Doc file StopList -> tap hop cac tu can loai bo
  2. Duyet tung file trong Dir (tru StopList)
  3. Voi moi tu trong file:
     - Chuyen ve chu thuong, bo dau cau
     - Bo qua neu trong StopList
     - Chi giu neu bat dau bang 'c'
     - Dem so lan xuat hien trong doc do
  4. Tra ve (DocTable, TermTable)
"""

import os
import re
import json


def CreateIndex(Dir: str, StopList: str) -> tuple:
    """
    Xay dung inverted index tu tat ca file trong Dir.

    Tham so:
        Dir      : duong dan den thu muc chua cac documents
        StopList : ten file stop list (nam trong Dir)

    Tra ve:
        (DocTable, TermTable)
        DocTable  = { doc_id (int) -> ten_file (str) }
        TermTable = { tu (str) -> { doc_id (int): so_lan (int) } }

    Rang buoc:
        - TermTable chi chua tu bat dau bang 'c' hoac 'C'
        - Khong chua cac tu trong StopList
    """

    stoplist_path = os.path.join(Dir, StopList)

    # ------------------------------------------------------------------
    # BUOC 1: Doc StopList
    # ------------------------------------------------------------------
    stop_words = set()
    if os.path.exists(stoplist_path):
        with open(stoplist_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    stop_words.add(word)
        print(f"[Indexer] Da doc {len(stop_words)} stop words.")
    else:
        print(f"[Indexer] Canh bao: Khong tim thay StopList tai '{stoplist_path}'")

    # ------------------------------------------------------------------
    # BUOC 2: Lay danh sach tat ca file trong Dir (tru StopList)
    # ------------------------------------------------------------------
    DocTable  = {}   # { doc_id -> ten_file }
    TermTable = {}   # { tu    -> { doc_id: so_lan } }

    try:
        all_files = sorted(os.listdir(Dir))
    except FileNotFoundError:
        print(f"[Indexer] Loi: Thu muc '{Dir}' khong ton tai.")
        return {}, {}

    # Chi lay file .txt, bo qua StopList va wordfile
    doc_files = [
        f for f in all_files
        if f.endswith(".txt") and f != StopList and f != "wordfile.txt"
    ]

    if not doc_files:
        print(f"[Indexer] Canh bao: Khong tim thay file .txt nao trong '{Dir}'")
        return {}, {}

    print(f"[Indexer] Tim thay {len(doc_files)} documents: {doc_files}")

    # ------------------------------------------------------------------
    # BUOC 3: Doc tung file, dem tan suat tung tu
    # ------------------------------------------------------------------
    for doc_id, filename in enumerate(doc_files):
        DocTable[doc_id] = filename
        filepath = os.path.join(Dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Tach tu: dung regex de lay chuoi chu cai va so
        # re.findall tra ve list cac tu phu hop pattern
        raw_words = re.findall(r"[a-zA-Z]+", text)

        for raw_word in raw_words:
            word = raw_word.lower()  # chuyen ve thuong de so sanh

            # Loai bo stop words
            if word in stop_words:
                continue

            # Chi giu tu bat dau bang 'c' (rang buoc cua bai tap)
            if not word.startswith("c"):
                continue

            # Them vao TermTable
            if word not in TermTable:
                TermTable[word] = {}

            if doc_id not in TermTable[word]:
                TermTable[word][doc_id] = 0

            TermTable[word][doc_id] += 1

    print(f"[Indexer] Da index {len(TermTable)} terms bat dau bang 'c'.")
    return DocTable, TermTable


def save_index(DocTable: dict, TermTable: dict, output_path: str):
    """
    Luu index xuong file JSON de tai su dung sau.

    Cau truc JSON:
    {
      "DocTable":  { "0": "doc1.txt", "1": "doc2.txt" },
      "TermTable": { "cartel": {"0": 2, "1": 1}, ... }
    }
    """
    # JSON chi cho phep key la string, nen ep kieu
    serializable = {
        "DocTable":  {str(k): v for k, v in DocTable.items()},
        "TermTable": {
            term: {str(doc_id): count for doc_id, count in postings.items()}
            for term, postings in TermTable.items()
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    print(f"[Indexer] Da luu index vao: {output_path}")


def load_index(index_path: str) -> tuple:
    """
    Tai index da luu tu file JSON.
    Ep key doc_id ve int de dung nhat quan voi phan con lai.
    """
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    DocTable = {int(k): v for k, v in data["DocTable"].items()}
    TermTable = {
        term: {int(doc_id): count for doc_id, count in postings.items()}
        for term, postings in data["TermTable"].items()
    }
    return DocTable, TermTable
