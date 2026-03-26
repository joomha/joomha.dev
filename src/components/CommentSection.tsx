import { useEffect, useRef, useState } from "react";
import {
  collection,
  addDoc,
  deleteDoc,
  doc,
  onSnapshot,
  orderBy,
  query,
  where,
  serverTimestamp,
  type Timestamp,
} from "firebase/firestore";
import { db } from "@/lib/firebase";

interface Comment {
  id: string;
  name: string;
  message: string;
  createdAt: Timestamp | null;
}

interface Props {
  postSlug: string;
}

const ADMIN_KEY = "jomha_admin_2026";

function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "baru saja";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} menit lalu`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} jam lalu`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} hari lalu`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} bulan lalu`;
  return `${Math.floor(months / 12)} tahun lalu`;
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

const AVATAR_COLORS = [
  "#0d9488",
  "#6366f1",
  "#ec4899",
  "#f59e0b",
  "#10b981",
  "#8b5cf6",
  "#ef4444",
  "#3b82f6",
];

function getAvatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

export default function CommentSection({ postSlug }: Props) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showAdminInput, setShowAdminInput] = useState(false);
  const [adminInput, setAdminInput] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Check admin status
  useEffect(() => {
    const stored = localStorage.getItem("jomha_admin");
    if (stored === ADMIN_KEY) {
      setIsAdmin(true);
    }
    // Restore saved name
    const savedName = localStorage.getItem("jomha_comment_name");
    if (savedName) setName(savedName);
  }, []);

  // Realtime listener
  useEffect(() => {
    const q = query(
      collection(db, "comments"),
      where("postSlug", "==", postSlug),
      orderBy("createdAt", "asc")
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const data: Comment[] = snapshot.docs.map((doc) => ({
          id: doc.id,
          name: doc.data().name,
          message: doc.data().message,
          createdAt: doc.data().createdAt,
        }));
        setComments(data);
        setLoading(false);
      },
      (error) => {
        console.error("Error fetching comments:", error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [postSlug]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !message.trim() || submitting) return;

    setSubmitting(true);
    try {
      await addDoc(collection(db, "comments"), {
        postSlug,
        name: name.trim(),
        message: message.trim(),
        createdAt: serverTimestamp(),
      });
      localStorage.setItem("jomha_comment_name", name.trim());
      setMessage("");
      // Scroll to bottom
      setTimeout(() => {
        listRef.current?.scrollTo({
          top: listRef.current.scrollHeight,
          behavior: "smooth",
        });
      }, 300);
    } catch (err) {
      console.error("Error adding comment:", err);
      alert("Gagal mengirim komentar. Coba lagi.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(commentId: string) {
    if (!confirm("Hapus komentar ini?")) return;
    setDeletingId(commentId);
    try {
      await deleteDoc(doc(db, "comments", commentId));
    } catch (err) {
      console.error("Error deleting comment:", err);
      alert("Gagal menghapus. Coba lagi.");
    } finally {
      setDeletingId(null);
    }
  }

  function handleAdminLogin() {
    if (adminInput === ADMIN_KEY) {
      localStorage.setItem("jomha_admin", ADMIN_KEY);
      setIsAdmin(true);
      setShowAdminInput(false);
      setAdminInput("");
    } else {
      alert("Key salah.");
    }
  }

  return (
    <section className="comment-section">
      <div className="comment-header">
        <h2 className="comment-title">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          Komentar{" "}
          {comments.length > 0 && (
            <span className="comment-count">{comments.length}</span>
          )}
        </h2>
        {!isAdmin && (
          <button
            type="button"
            className="admin-toggle"
            onClick={() => setShowAdminInput(!showAdminInput)}
            title="Admin login"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </button>
        )}
        {isAdmin && (
          <span className="admin-badge">Admin</span>
        )}
      </div>

      {showAdminInput && (
        <div className="admin-input-row">
          <input
            type="password"
            placeholder="Admin key..."
            value={adminInput}
            onChange={(e) => setAdminInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAdminLogin()}
            className="admin-input"
          />
          <button
            type="button"
            onClick={handleAdminLogin}
            className="admin-btn"
          >
            OK
          </button>
        </div>
      )}

      {/* Comment List */}
      <div className="comment-list" ref={listRef}>
        {loading && (
          <div className="comment-loading">
            <div className="spinner" />
            <span>Memuat komentar...</span>
          </div>
        )}

        {!loading && comments.length === 0 && (
          <div className="comment-empty">
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ opacity: 0.3 }}
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>Belum ada komentar. Jadilah yang pertama!</p>
          </div>
        )}

        {comments.map((comment) => (
          <div
            key={comment.id}
            className={`comment-item ${deletingId === comment.id ? "deleting" : ""}`}
          >
            <div
              className="comment-avatar"
              style={{ backgroundColor: getAvatarColor(comment.name) }}
            >
              {getInitials(comment.name)}
            </div>
            <div className="comment-body">
              <div className="comment-meta">
                <span className="comment-name">{comment.name}</span>
                <span className="comment-time">
                  {comment.createdAt
                    ? timeAgo(comment.createdAt.toDate())
                    : "baru saja"}
                </span>
              </div>
              <p className="comment-message">{comment.message}</p>
            </div>
            {isAdmin && (
              <button
                type="button"
                className="delete-btn"
                onClick={() => handleDelete(comment.id)}
                disabled={deletingId === comment.id}
                title="Hapus komentar"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="comment-form">
        <div className="form-row">
          <input
            type="text"
            placeholder="Nama kamu"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={50}
            required
            className="input-name"
          />
        </div>
        <div className="form-row form-message-row">
          <textarea
            placeholder="Tulis komentar..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={1000}
            required
            rows={3}
            className="input-message"
          />
          <button
            type="submit"
            disabled={submitting || !name.trim() || !message.trim()}
            className="submit-btn"
          >
            {submitting ? (
              <div className="spinner small" />
            ) : (
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>
        <span className="char-count">
          {message.length}/1000
        </span>
      </form>
    </section>
  );
}
