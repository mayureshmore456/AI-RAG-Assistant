import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";


function App() {

  // =========================================================
  // AUTH
  // =========================================================

  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [isLogin, setIsLogin] = useState(true);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [user, setUser] = useState(() => {

    const savedUser =
      localStorage.getItem("user");

    return savedUser
      ? JSON.parse(savedUser)
      : null;
  });


  // =========================================================
  // CHAT
  // =========================================================

  const [chats, setChats] = useState([]);

  const [currentChatId, setCurrentChatId] =
    useState(null);

  const [messages, setMessages] =
    useState([]);

  const [question, setQuestion] =
    useState("");

  const [sendingMessage, setSendingMessage] =
    useState(false);

  const [loadingChats, setLoadingChats] =
    useState(false);

  const [loadingMessages, setLoadingMessages] =
    useState(false);


  // =========================================================
  // DOCUMENTS
  // =========================================================

  const [documents, setDocuments] =
    useState([]);

  const [showDocuments, setShowDocuments] =
    useState(false);

  const [loadingDocuments, setLoadingDocuments] =
    useState(false);

  const [uploadingPDF, setUploadingPDF] =
    useState(false);

  const [deletingDocumentId, setDeletingDocumentId] =
    useState(null);

  const fileInputRef =
    useRef(null);


  // =========================================================
  // LOAD CHATS
  // =========================================================

  const loadChats = async () => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) return;

    setLoadingChats(true);

    try {

      const response = await fetch(
        `${API_URL}/chats`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Failed to load chats."
        );
      }

      setChats(
        data.chats || []
      );

    } catch (error) {

      console.error(error);

      setMessage(
        error.message
      );

    } finally {

      setLoadingChats(false);
    }
  };


  // =========================================================
  // LOAD DOCUMENTS
  // =========================================================

  const loadDocuments = async () => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) return;

    setLoadingDocuments(true);

    try {

      const response =
        await fetch(
          `${API_URL}/documents`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Failed to load documents."
        );
      }

      setDocuments(
        data.documents || []
      );

    } catch (error) {

      console.error(error);

      setMessage(
        error.message
      );

    } finally {

      setLoadingDocuments(false);
    }
  };


  // =========================================================
  // LOAD INITIAL DATA
  // =========================================================

  useEffect(() => {

    if (isLoggedIn) {

      loadChats();

      loadDocuments();
    }

  }, [isLoggedIn]);


  // =========================================================
  // LOGIN / REGISTER
  // =========================================================

  const handleSubmit = async (e) => {

    e.preventDefault();

    setMessage("");

    setLoading(true);

    try {

      const endpoint =
        isLogin
          ? `${API_URL}/auth/login`
          : `${API_URL}/auth/register`;

      const body =
        isLogin
          ? {
              email,
              password,
            }
          : {
              name,
              email,
              password,
            };

      const response =
        await fetch(
          endpoint,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify(
              body
            ),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Something went wrong."
        );
      }

      if (isLogin) {

        localStorage.setItem(
          "access_token",
          data.access_token
        );

        localStorage.setItem(
          "user",
          JSON.stringify(
            data.user
          )
        );

        setUser(data.user);

        setIsLoggedIn(true);

        setMessage("");

      } else {

        setMessage(
          "Registration successful. Please login."
        );

        setIsLogin(true);

        setName("");

        setPassword("");
      }

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setLoading(false);
    }
  };


  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    setUser(null);

    setIsLoggedIn(false);

    setChats([]);

    setDocuments([]);

    setMessages([]);

    setCurrentChatId(null);
  };


  // =========================================================
  // CREATE CHAT
  // =========================================================

  const handleNewChat = async () => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {

      setMessage(
        "Please login first."
      );

      return;
    }

    try {

      const response =
        await fetch(
          `${API_URL}/chats`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              title: "New Chat",
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Failed to create chat."
        );
      }

      setChats(
        previous => [
          data,
          ...previous,
        ]
      );

      setCurrentChatId(
        data.id
      );

      setMessages([]);

      setQuestion("");

      setMessage("");

    } catch (error) {

      setMessage(
        error.message
      );
    }
  };


  // =========================================================
  // SELECT CHAT
  // =========================================================

  const handleSelectChat = async (
    chatId
  ) => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    setCurrentChatId(
      chatId
    );

    setMessages([]);

    setLoadingMessages(true);

    try {

      const response =
        await fetch(
          `${API_URL}/chats/${chatId}`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Failed to load chat."
        );
      }

      setMessages(
        data.messages || []
      );

    } catch (error) {

      setMessage(
        error.message
      );

    } finally {

      setLoadingMessages(false);
    }
  };


  // =========================================================
  // OPEN FILE PICKER
  // =========================================================

  const handleUploadClick = () => {

    if (!currentChatId) {

      setMessage(
        "Create a chat first."
      );

      return;
    }

    fileInputRef.current?.click();
  };


  // =========================================================
  // UPLOAD PDF
  // =========================================================

  const handleFileChange = async (
    event
  ) => {

    const file =
      event.target.files?.[0];

    if (!file) return;

    if (
      file.type !==
      "application/pdf"
    ) {

      setMessage(
        "Only PDF files are allowed."
      );

      event.target.value = "";

      return;
    }

    const token =
      localStorage.getItem(
        "access_token"
      );

    setUploadingPDF(true);

    setMessage("");

    try {

      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      const response =
        await fetch(
          `${API_URL}/upload`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },

            body: formData,
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "PDF upload failed."
        );
      }

      setMessage(
        `Uploaded ${data.filename} successfully.`
      );

      await loadDocuments();

    } catch (error) {

      console.error(error);

      setMessage(
        error.message
      );

    } finally {

      setUploadingPDF(false);

      event.target.value = "";
    }
  };


  // =========================================================
  // DELETE DOCUMENT
  // =========================================================

  const handleDeleteDocument = async (
    documentId
  ) => {

    const confirmed =
      window.confirm(
        "Delete this document? Its vector chunks will also be deleted."
      );

    if (!confirmed) return;

    const token =
      localStorage.getItem(
        "access_token"
      );

    setDeletingDocumentId(
      documentId
    );

    try {

      const response =
        await fetch(
          `${API_URL}/documents/${documentId}`,
          {
            method: "DELETE",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Failed to delete document."
        );
      }

      setDocuments(
        previous =>
          previous.filter(
            document =>
              document.id !==
              documentId
          )
      );

      setMessage(
        "Document deleted successfully."
      );

    } catch (error) {

      console.error(error);

      setMessage(
        error.message
      );

    } finally {

      setDeletingDocumentId(
        null
      );
    }
  };


  // =========================================================
  // SEND MESSAGE
  // =========================================================

  const handleSendMessage =
    async () => {

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!currentChatId) {

        setMessage(
          "Create a chat first."
        );

        return;
      }

      const trimmedQuestion =
        question.trim();

      if (!trimmedQuestion)
        return;

      setSendingMessage(true);

      setMessage("");

      const temporaryMessage = {

        id:
          `temp-${Date.now()}`,

        chat_id:
          currentChatId,

        role:
          "user",

        content:
          trimmedQuestion,

        created_at:
          new Date().toISOString(),
      };

      setMessages(
        previous => [
          ...previous,
          temporaryMessage,
        ]
      );

      setQuestion("");

      try {

        const params =
          new URLSearchParams();

        params.append(
          "question",
          trimmedQuestion
        );

        params.append(
          "chat_id",
          currentChatId
        );

        const response =
          await fetch(
            `${API_URL}/chat?${params}`,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        const data =
          await response.json();

        if (!response.ok) {

          throw new Error(
            data.detail ||
              "Failed to get AI response."
          );
        }

        setMessages(
          previous => {

            const filtered =
              previous.filter(
                msg =>
                  msg.id !==
                  temporaryMessage.id
              );

            return [
              ...filtered,
              data.user_message,
              data.assistant_message,
            ];
          }
        );

        await loadChats();

      } catch (error) {

        console.error(error);

        setMessages(
          previous =>
            previous.filter(
              msg =>
                msg.id !==
                temporaryMessage.id
            )
        );

        setMessage(
          error.message
        );

      } finally {

        setSendingMessage(false);
      }
    };


  // =========================================================
  // ENTER TO SEND
  // =========================================================

  const handleInputKeyDown = (
    event
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      if (!sendingMessage) {

        handleSendMessage();
      }
    }
  };


  // =========================================================
  // LOGIN SCREEN
  // =========================================================

  if (!isLoggedIn) {

    return (

      <div className="app">

        <div className="auth-container">

          <div className="auth-card">

            <div className="logo">
              AI
            </div>

            <h1>
              AI RAG Assistant
            </h1>

            <p className="subtitle">
              {isLogin
                ? "Welcome back. Login to continue."
                : "Create your account to get started."}
            </p>

            <form
              onSubmit={
                handleSubmit
              }
            >

              {!isLogin && (

                <div className="input-group">

                  <label>
                    Name
                  </label>

                  <input
                    type="text"
                    value={name}
                    placeholder="Enter your name"
                    onChange={
                      e =>
                        setName(
                          e.target.value
                        )
                    }
                    required
                  />

                </div>
              )}

              <div className="input-group">

                <label>
                  Email
                </label>

                <input
                  type="email"
                  value={email}
                  placeholder="Enter your email"
                  onChange={
                    e =>
                      setEmail(
                        e.target.value
                      )
                  }
                  required
                />

              </div>

              <div className="input-group">

                <label>
                  Password
                </label>

                <input
                  type="password"
                  value={password}
                  placeholder="Enter your password"
                  onChange={
                    e =>
                      setPassword(
                        e.target.value
                      )
                  }
                  required
                />

              </div>

              <button
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Please wait..."
                  : isLogin
                  ? "Login"
                  : "Create Account"}
              </button>

            </form>

            {message && (

              <div className="message">
                {message}
              </div>
            )}

            <div className="switch">

              {isLogin
                ? "Don't have an account?"
                : "Already have an account?"}

              <button
                className="switch-button"
                onClick={() => {

                  setIsLogin(
                    !isLogin
                  );

                  setMessage("");
                }}
              >
                {isLogin
                  ? "Create one"
                  : "Login"}
              </button>

            </div>

          </div>

        </div>

      </div>
    );
  }


  // =========================================================
  // MAIN APPLICATION
  // =========================================================

  return (

    <div className="dashboard">

      {/* ================================================= */}
      {/* FIXED SIDEBAR */}
      {/* ================================================= */}

      <aside className="sidebar">

        <div className="sidebar-header">

          <div className="brand-icon">
            AI
          </div>

          <div>

            <h2>
              AI RAG
            </h2>

            <span>
              Assistant
            </span>

          </div>

        </div>


        <button
          className="new-chat-button"
          onClick={
            handleNewChat
          }
        >
          + New Chat
        </button>


        <div className="sidebar-section">

          <p className="section-title">
            RECENT CHATS
          </p>

          {loadingChats ? (

            <p className="empty-chats">
              Loading chats...
            </p>

          ) : chats.length === 0 ? (

            <p className="empty-chats">
              No chats yet.
            </p>

          ) : (

            chats.map(
              chat => (

                <div
                  key={chat.id}
                  className={
                    `chat-item ${
                      currentChatId ===
                      chat.id
                        ? "active"
                        : ""
                    }`
                  }
                  onClick={() =>
                    handleSelectChat(
                      chat.id
                    )
                  }
                >

                  <span className="chat-symbol">
                    +
                  </span>

                  <span>
                    {chat.title}
                  </span>

                </div>
              )
            )
          )}

        </div>


        <div className="sidebar-bottom">

          <button
            className="sidebar-button"
            onClick={() => {

              setShowDocuments(
                !showDocuments
              );

              loadDocuments();
            }}
          >
            Documents
          </button>


          <button
            className="sidebar-button"
            onClick={
              handleLogout
            }
          >
            Logout
          </button>

        </div>

      </aside>


      {/* ================================================= */}
      {/* MAIN */}
      {/* ================================================= */}

      <main className="main-content">

        <header className="topbar">

          <div>

            <h1>
              AI RAG Assistant
            </h1>

            <p>
              Ask questions about your documents
            </p>

          </div>


          <div className="user-info">

            <div className="avatar">

              {user?.name
                ?.charAt(0)
                .toUpperCase() ||
                "U"}

            </div>

            <div>

              <strong>
                {user?.name}
              </strong>

              <span>
                {user?.email}
              </span>

            </div>

          </div>

        </header>


        {/* ================================================= */}
        {/* DOCUMENT PANEL */}
        {/* ================================================= */}

        {showDocuments && (

          <div className="documents-panel">

            <div className="documents-header">

              <div>

                <h2>
                  Documents
                </h2>

                <p>
                  Your uploaded PDFs
                </p>

              </div>

              <button
                className="close-button"
                onClick={() =>
                  setShowDocuments(
                    false
                  )
                }
              >
                Close
              </button>

            </div>


            <div className="document-upload-area">

              <button
                className="upload-main-button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={
                  uploadingPDF
                }
              >
                {uploadingPDF
                  ? "Processing..."
                  : "Upload PDF"}
              </button>

              <p>
                Upload a PDF to add it
                to your knowledge base.
              </p>

            </div>


            <div className="document-list">

              {loadingDocuments ? (

                <p>
                  Loading documents...
                </p>

              ) : documents.length === 0 ? (

                <div className="no-documents">
                  <h3>
                    No documents yet
                  </h3>

                  <p>
                    Upload your first PDF
                    to get started.
                  </p>
                </div>

              ) : (

                documents.map(
                  document => (

                    <div
                      className="document-card"
                      key={
                        document.id
                      }
                    >

                      <div className="document-info">

                        <div className="document-icon">
                          PDF
                        </div>

                        <div>

                          <strong>
                            {
                              document.filename
                            }
                          </strong>

                          <span>
                            {
                              document.chunk_count
                            } chunks
                          </span>

                        </div>

                      </div>


                      <button
                        className="delete-button"
                        onClick={() =>
                          handleDeleteDocument(
                            document.id
                          )
                        }
                        disabled={
                          deletingDocumentId ===
                          document.id
                        }
                      >
                        {deletingDocumentId ===
                        document.id
                          ? "..."
                          : "Delete"}
                      </button>

                    </div>
                  )
                )
              )}

            </div>

          </div>
        )}


        {/* Hidden upload input */}

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={
            handleFileChange
          }
          style={{
            display: "none"
          }}
        />


        {/* ================================================= */}
        {/* CHAT AREA */}
        {/* ================================================= */}

        <section className="chat-area">

          {currentChatId ? (

            <div className="conversation">

              {loadingMessages ? (

                <div className="loading-messages">
                  Loading conversation...
                </div>

              ) : messages.length === 0 ? (

                <div className="empty-conversation">

                  <div className="welcome-icon">
                    AI
                  </div>

                  <h2>
                    New conversation
                  </h2>

                  <p>
                    Upload a PDF and ask
                    questions about it.
                  </p>

                </div>

              ) : (

                messages.map(
                  msg => (

                    <div
                      key={msg.id}
                      className={
                        `message-row ${
                          msg.role === "user"
                            ? "user-message-row"
                            : "assistant-message-row"
                        }`
                      }
                    >

                      <div
                        className={
                          `message-avatar ${
                            msg.role === "user"
                              ? "user-avatar"
                              : "assistant-avatar"
                          }`
                        }
                      >
                        {msg.role === "user"
                          ? user?.name
                              ?.charAt(0)
                              .toUpperCase()
                          : "AI"}
                      </div>


                      <div
                        className={
                          `message-bubble ${
                            msg.role === "user"
                              ? "user-message"
                              : "assistant-message"
                          }`
                        }
                      >

                        <div className="message-role">

                          {msg.role === "user"
                            ? "You"
                            : "AI Assistant"}

                        </div>

                        <div className="message-content">

                          {msg.content}

                        </div>

                      </div>

                    </div>
                  )
                )
              )}

            </div>

          ) : (

            <div className="welcome-section">

              <div className="welcome-icon">
                AI
              </div>

              <h2>
                What can I help you with?
              </h2>

              <p>
                Create a chat and upload
                a PDF to get started.
              </p>

              <div className="suggestion-grid">

                <div className="suggestion-card">

                  <span>
                    01
                  </span>

                  <strong>
                    Upload a document
                  </strong>

                  <p>
                    Add a PDF to your
                    knowledge base.
                  </p>

                </div>


                <div className="suggestion-card">

                  <span>
                    02
                  </span>

                  <strong>
                    Ask a question
                  </strong>

                  <p>
                    Search your documents
                    using natural language.
                  </p>

                </div>


                <div className="suggestion-card">

                  <span>
                    03
                  </span>

                  <strong>
                    Get an answer
                  </strong>

                  <p>
                    Receive answers grounded
                    in your documents.
                  </p>

                </div>

              </div>

            </div>
          )}

        </section>


        {/* ================================================= */}
        {/* INPUT */}
        {/* ================================================= */}

        <div className="input-area">

          {message && (

            <div className="chat-error">
              {message}
            </div>
          )}


          <div className="input-wrapper">

            <button
              className="attachment-button"
              onClick={
                handleUploadClick
              }
              disabled={
                !currentChatId ||
                uploadingPDF
              }
            >
              {uploadingPDF
                ? "..."
                : "+"}
            </button>


            <textarea
              placeholder={
                currentChatId
                  ? "Ask something about your document..."
                  : "Create a chat first..."
              }
              value={question}
              onChange={
                e =>
                  setQuestion(
                    e.target.value
                  )
              }
              onKeyDown={
                handleInputKeyDown
              }
              disabled={
                !currentChatId ||
                sendingMessage
              }
              rows="1"
            />


            <button
              className="send-button"
              onClick={
                handleSendMessage
              }
              disabled={
                !currentChatId ||
                !question.trim() ||
                sendingMessage
              }
            >
              {sendingMessage
                ? "..."
                : "Send"}
            </button>

          </div>


          <p className="input-hint">
            Enter to send. Shift + Enter
            for a new line.
          </p>

        </div>

      </main>

    </div>
  );
}

export default App;