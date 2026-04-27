import Link from "next/link";

export default function Layout({ children, title = "SignalFeed" }) {
  return (
    <div className="page-shell">
      <header className="topbar">
        <div>
          <h1>{title}</h1>
          <p>High-signal updates from founders, CEOs, and communities.</p>
        </div>
        <nav>
          <Link href="/">Feed</Link>
          <Link href="/sources">Sources</Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
