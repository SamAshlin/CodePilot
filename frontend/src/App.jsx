import { useState } from "react";
import axios from "axios";
import "./App.css";
import API_URL from "./api";

function App() {

  const [githubUrl, setGithubUrl] = useState("");
  const [repositoryId, setRepositoryId] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const [citations, setCitations] = useState([]);

  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);

  const [error, setError] = useState("");


  // -----------------------------------------
  // Index repository
  // -----------------------------------------

  const indexRepository = async () => {

    if (!githubUrl.trim()) {
      setError("Enter a GitHub repository URL.");
      return;
    }

    setError("");
    setIndexing(true);

    try {

      const response = await axios.post(
        `${API_URL}/api/repositories/index`,
        {
          github_url: githubUrl.trim()
        }
      );

      setRepositoryId(
        response.data.repository_id
      );

    } catch (error) {

      console.error(
        "Indexing error:",
        error
      );

      setError(
        error.response?.data?.detail ||
        "Repository indexing failed."
      );

    } finally {

      setIndexing(false);
    }
  };


  // -----------------------------------------
  // Ask question
  // -----------------------------------------

  const askQuestion = async () => {

    if (!repositoryId) {
      setError("Index a repository before asking a question.");
      return;
    }

    if (!question.trim()) {
      setError("Enter a question about the repository.");
      return;
    }

    setError("");
    setLoading(true);

    try {

      const response = await axios.post(
        `${API_URL}/api/chat/`,
        {
          repository_id: repositoryId,
          question: question.trim()
        }
      );

      setAnswer(
        response.data.answer
      );

      setCitations(
        response.data.citations || []
      );

    } catch (error) {

      console.error(
        "Chat error:",
        error
      );

      setError(
        error.response?.data?.detail ||
        "Failed to generate an answer."
      );

    } finally {

      setLoading(false);
    }
  };


  return (

    <div className="app">

      {/* =====================================
          HEADER
      ===================================== */}

      <header className="header">

        <div className="header-inner">

          <div className="brand">

            <div className="brand-icon">
              ◈
            </div>

            <div>

              <h1>
                CodePilot
              </h1>

              <p>
                AI-powered codebase understanding
              </p>

            </div>

          </div>

          <div className="header-badge">
            AI CODE ASSISTANT
          </div>

        </div>

      </header>


      {/* =====================================
          MAIN
      ===================================== */}

      <main className="main">


        {/* ===================================
            REPOSITORY
        =================================== */}

        <section className="section">

          <div className="section-header">

            <div>

              <h2 className="section-title">
                Repository
              </h2>

              <p className="section-description">
                Connect a public GitHub repository
                to analyze its codebase.
              </p>

            </div>

          </div>


          <div className="section-content">

            <div className="repository-input-row">

              <div className="repository-input-wrapper">

                <span className="repository-input-icon">
                  ◇
                </span>

                <input
                  className="repository-input"
                  type="text"
                  placeholder="https://github.com/user/repository"
                  value={githubUrl}
                  onChange={(e) =>
                    setGithubUrl(e.target.value)
                  }
                />

              </div>


              <button
                className="primary-button"
                onClick={indexRepository}
                disabled={indexing}
              >

                {indexing
                  ? "Indexing..."
                  : "Index Repository"
                }

              </button>

            </div>


            {repositoryId && (

              <div className="repository-status">

                <span className="status-dot" />

                Repository indexed and ready

              </div>

            )}

          </div>

        </section>


        {/* ===================================
            QUESTION
        =================================== */}

        <section className="section">

          <div className="section-header">

            <div>

              <h2 className="section-title">
                Ask about your code
              </h2>

              <p className="section-description">
                Ask questions about architecture,
                functions, authentication, APIs,
                or implementation details.
              </p>

            </div>

          </div>


          <div className="section-content">

            <div className="question-area">

              <textarea
                className="question-input"
                placeholder="Where is authentication implemented?"
                value={question}
                onChange={(e) =>
                  setQuestion(e.target.value)
                }
              />

            </div>


            <div className="question-footer">

              <span className="question-hint">
                Answers are grounded in the indexed repository.
              </span>

              <button
                className="primary-button ask-button"
                onClick={askQuestion}
                disabled={loading || !repositoryId}
              >

                {loading
                  ? "Analyzing..."
                  : "Ask Codebase"
                }

              </button>

            </div>

          </div>

        </section>


        {/* ===================================
            ERROR
        =================================== */}

        {error && (

          <div
            style={{
              marginBottom: "20px",
              padding: "12px 14px",
              border: "1px solid rgba(239,68,68,0.25)",
              borderRadius: "9px",
              background: "rgba(239,68,68,0.08)",
              color: "#fca5a5",
              fontSize: "13px"
            }}
          >

            {error}

          </div>

        )}


        {/* ===================================
            RESULTS
        =================================== */}

        {answer && (

          <section className="results">

            <div className="results-grid">


              {/* =============================
                  ANSWER
              ============================== */}

              <div className="answer-card">

                <div className="card-header">

                  <h3 className="card-title">
                    Answer
                  </h3>

                  <span className="ai-label">
                    AI GENERATED
                  </span>

                </div>


                <div className="answer-content">

                  {answer}

                </div>

              </div>


              {/* =============================
                  SOURCES
              ============================== */}

              <div className="sources-card">

                <div className="card-header">

                  <h3 className="card-title">
                    Sources
                  </h3>

                  <span className="ai-label">
                    {citations.length}
                  </span>

                </div>


                {citations.length > 0 ? (

                  <div className="sources-list">

                    {citations.map(
                      (citation, index) => (

                        <div
                          className="citation"
                          key={index}
                        >

                          <div className="citation-file">

                            <span className="file-icon">
                              ◇
                            </span>

                            {citation.file}

                          </div>

                          <div className="citation-meta">

                            Lines{" "}
                            {citation.start_line}
                            {" – "}
                            {citation.end_line}

                          </div>

                        </div>

                      )
                    )}

                  </div>

                ) : (

                  <div className="empty-sources">
                    No source references available.
                  </div>

                )}

              </div>

            </div>

          </section>

        )}

      </main>


      {/* =====================================
          FOOTER
      ===================================== */}

      <footer className="footer">

        CodePilot · AI-powered repository analysis

      </footer>

    </div>

  );
}

export default App;