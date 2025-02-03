

- Feature to access the pre generated "vector embeddings"
  Instead of creating the embeddings again and again.

- some of the documents, have images not pdf's themselves,
  The text cannot be selected. How do I process such documents?

  - a program to convert these images containing texts,
    program that can extract all sorts of text's out of them

* Less time consuming

- Test and ensure that the retrieved information is relevant
  to the query

* Higher accuracy

- Check out how these responses by themselves can be returned to
  the user. In a more readable format.

* Real work application

- add Tiny LLama in between , check out how connections would be formed

* Return a coherent response to the user via Flask API.

- Expose Flask API endpoints (/embed, /query).
  Connect frontend to backend (React, or simple CLI testing first).

* Proper User's interface instead of it being a command line

- Then will check out , How to bring in LLama in all this

This is my backend code till now , for the multilingual chatbot
that I was talking about with you

# The updates that I need to make and in what order :

- Need to be able to extract texts from pdf files meaningfully.
  Some pdf files consist of images with text written in it that
  cannot be selected, I need to be able to extract text from those
  files as well.

- Then the text needs to be stored properly along with their embeddings.
  When running the program at first it should create embeddings
  and process the documents from the start. Then on subsequent runs
  it should just use the files that were processed previously

  (here process meaning texts were extracted and vector embeddings were
  created)

- Then once all that is done, and I can print the extracted text.
  Then I will use "flask" and through api endpoints send a query.
  will use postman for that, with the intention of receiving "texts"
  from documents as the response. Not just any random text,
  but text which is relevant my query.

- Then my query (I think) would be converted into vector embeddings,
  and the "block of text" which seems the most similar to my query
  would be found via vector similarity search and given as a response to me.

  (Now I don't know wether I will be fetched accurate responses just on
  the basis of that, or will I need a LLM or framework like "rasa" which
  send a proper query to the database in order to get its "context" with
  which the response would be sent back to the customer.)

  well for now I just intend to keep the functionality to getting
  proper segments of information (along with metadata) based on user query.

  And the output/response sent should be readable.
  for now all of this will take place in the terminal.
  And then an interface will need to be designed where user can enter his/her
  information and see the output on the screen , as a document

- Later on I will try to make it as a "chat bot" will have to include
  Rasa framework along with a lightweight LLM as the brain, which would
  create those responses.

  Add those in between for creating coherent responses and sending them
  to the user.

- Then there is also the fact that user's query can be in either
  english/ hindi or a mix of both. despite that the correct information needs
  to be fetched

- In the intial stages its just

  user query -> sent to backend
  backend response -> sent back to the user (via an interface)

  then with the addition of features such as multilingual
  capabilities, and responses to the user in "human like"
  understandable manner, new layers of LLM and frameworks like
  Rasa will need to be introduces I suppose to make it happen

  then the functioning would be more like:

  user query -> RASA interprets entity and intent
  RASA then calls the LLM sends it cleaner message that LLM can understand ->
  LLM then understands it -> calls for backend to get relevant documents

  Backend sends the information -> LLM recieves it, generates a textual
  response around that received information -> sends it to the user interface
  -> user sees the message, and asks further questions

  The cycle repeats

# the error:

Message in the terminal, along with the error:

OLDER DOCUMENTS EXIST  
Checking files:
DB exists: True
FAISS index exists: True  
JSON config exists: True  
Loading existing FAISS index...
Error loading existing index: The number of documents in the SQL database (40) doesn't match the number of embeddings in FAISS (0). Make sure your FAISS configuration file points to the same database that you used when you saved the original index.

The code part due to which the index and docs aren't being stored properly, I think:

# Save both the document store and the FAISS index

            print("Saving index...")
            os.makedirs("./faiss_data", exist_ok=True)
            document_store.save(
                index_path="./faiss_data/faiss_index"
            )

The code part which causes the error:

document_store.load(
index_path="./faiss_data/faiss_index"
)

Question from my side:

There are three files that are generated each time I run this code:

one - faiss_document_store.db
second - faiss_index - (not extension)
third - faiss_index.json

so are the stored documents , which consist of text , stored in faiss_document_store.db?

while the vector index values per document is stored in faiss_index? and they are both somehow connected to eachother? Like each document refers to its respective vectore index?
