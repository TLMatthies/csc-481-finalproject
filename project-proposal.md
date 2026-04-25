# **Project Proposal**

## *Dance, Dance, Resolution*

**Team Members:**
Briana Kirkman, Timothy Matthies, Pragati Toppo

---

## **1. Overview**

Our plan is to encode our own knowledge of the dance clubs on campus and create a natural language interface for users to interact with and ask questions. A general use case might be someone looking for a dance club to join, but not sure which ones fit their wants and needs.

---

## **2. Problem Description**

Cal Poly Now is the go-to directory for student orgs, but it's often outdated, inactive clubs stay listed while newer groups that have performed at events like Illuminate aren't there at all. Meeting times, audition info, and contacts change every quarter and rarely get updated. If you're not already on the right Discord server or following the right Instagram, it's genuinely hard to find this stuff.
The goal is to build a knowledge base of Cal Poly's cultural dance clubs and wrap a natural language interface around it, so students can just ask questions and get accurate answers without needing to already be plugged in. We'll build the KB from scratch using Cal Poly Now, the Illuminate showcase directory, and our own firsthand knowledge as people involved in the dance community. No existing tool does this, ChatGPT and similar models don't have this kind of local, specific data and will just make things up. Our starting point is a RAG^2^ setup with an LLM handling the natural language side and tool calls^1^ into our KB.

---

## **3. Knowledge Representation**

Our system will handle knowledge pertaining to the different cultural dance clubs at Cal Poly. There are a total of 19 different clubs and our knowledge base will handle information about performances, time commitments, dues, and more represented with prolog. We will be building this knowledge base from scratch using Cal Poly Now, the illuminate showcase directory, official club pages, and personal experience.

---

## **4. Methods and Tools**

For the knowledge base, we will most likely use manual input, possibly assisted by agentic AI, in Prolog^3^ or some similar knowledge encoding language. For the natural language interface, we will probably utilize an LLM and make available tool calls^1^ for Retrieval-Augmented Generation^2^.

---

## **5. Evaluation Criteria**

There are a few options for validation. For a lower effort, internal testing method, we can have some queries that we know the answers to. We can run these queries and see if the system responds accurately. If we wanted to involve other parties, we might be able to do a small user study and ask people to interact with the model. We could ask for qualitative or quantitative feedback on their experience.

---

## **6. References**

* Fwolf. (n.d.). *What is RAG? What are tool calls? And why is this important?*
  [https://www.fwolf.io/blog/llm-rag-tool-calls](https://www.fwolf.io/blog/llm-rag-tool-calls)

* Microsoft. (2025). *RAG time journey 1: RAG and knowledge retrieval fundamentals.*
  [https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/rag-time-journey-1-rag-and-knowledge-retrieval-fundamentals/4390174](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/rag-time-journey-1-rag-and-knowledge-retrieval-fundamentals/4390174)

* Fodor, P., Lally, A., & Ferrucci, D. (2008). *The Prolog interface to the unstructured information management architecture.*
  [https://arxiv.org/pdf/0809.0680](https://arxiv.org/pdf/0809.0680)

---

## **7. Knowledge Sources**

* Campus organization directory:
  [https://now.calpoly.edu/](https://now.calpoly.edu/)

* Illuminate 2026 program:
  [https://umv.mt/i26prog/](https://umv.mt/i26prog/)

* Lanternfest (clubs + performances):
  [https://www.instagram.com/lanternfestivalslo/?hl=en](https://www.instagram.com/lanternfestivalslo/?hl=en)

* Culturefest (clubs + performances):
  [https://www.instagram.com/calpoly_mcc/](https://www.instagram.com/calpoly_mcc/)



