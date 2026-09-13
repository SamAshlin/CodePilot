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


  // -----------------------------------------
  // Index GitHub repository
  // -----------------------------------------

  const indexRepository = async () => {

    if (!githubUrl) {
      alert("Enter a GitHub repository URL");
      return;
    }

    setIndexing(true);

    try {

      const response = await axios.post(
        `${API_URL}/api/repositories/index`,
        {
          github_url: githubUrl
        }
      );

      setRepositoryId(
        response.data.repository_id
      );

      alert(
        response.data.message ||
        `Indexed ${response.data.files} files`
      );

    } catch (error) {

      console.error(
        "Indexing error:",
        error
      );

      alert(
        error.response?.data?.detail ||
        "Indexing failed"
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
      alert("Index a repository first");
      return;
    }

    if (!question.trim()) {
      alert("Enter a question");
      return;
    }

    setLoading(true);

    try {

      const response = await axios.post(
        `${API_URL}/api/chat/`,
        {
          repository_id: repositoryId,
          question: question
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

      alert(
        error.response?.data?.detail ||
        "Failed to get answer"
      );

    } finally {

      setLoading(false);
    }
  };


  return (
    <div className="app">

      <header>

        <h1>
          Codebase RAG Assistant
        </h1>

        <p>
          Ask questions about your GitHub repository
        </p>

      </header>


      {/* ---------------------------------- */}
      {/* Repository Section */}
      {/* ---------------------------------- */}

      <section className="repository">

        <h2>
          Repository
        </h2>

        <div className="input-row">

          <input
            type="text"
            placeholder="https://github.com/user/repository"
            value={githubUrl}
            onChange={(e) =>
              setGithubUrl(e.target.value)
            }
          />

          <button
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

          <p className="success">

            Repository ready

          </p>

        )}

      </section>


      {/* ---------------------------------- */}
      {/* Chat Section */}
      {/* ---------------------------------- */}

      <section className="chat">

        <h2>
          Ask about the code
        </h2>

        <textarea
          placeholder="Where is authentication implemented?"
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
        />


        <button
          onClick={askQuestion}
          disabled={loading}
        >

          {loading
            ? "Thinking..."
            : "Ask"
          }

        </button>


        {/* -------------------------------- */}
        {/* Answer */}
        {/* -------------------------------- */}

        {answer && (

          <div className="answer">

            <h3>
              Answer
            </h3>

            <p>
              {answer}
            </p>


            <h3>
              Relevant Files
            </h3>


            {citations.length > 0 ? (

              citations.map(
                (citation, index) => (

                  <div
                    className="citation"
                    key={index}
                  >

                    <div>
                      📄 {citation.file}
                    </div>

                    <span>
                      Lines{" "}
                      {citation.start_line}-
                      {citation.end_line}
                    </span>

                  </div>

                )
              )

            ) : (

              <p>
                No citations available.
              </p>

            )}

          </div>

        )}

      </section>

    </div>
  );
}


export default App;