// src/views/HomeView.jsx
function HomeView({ onChangeView }) {
  return (
    <main className="home-view">
      {/* Login row */}
      <section className="home-login-row">
        <span className="home-login-label">CtCLink Sign In:</span>
        <input
          type="text"
          placeholder="Username / Student ID #"
          className="home-login-input"
        />
        <input
          type="password"
          placeholder="Password"
          className="home-login-input"
        />
        <button className="home-login-button">
          Login
        </button>
      </section>

      {/* Main tiles */}
      <section className="home-tiles">
        <button
          className="home-tile home-tile-requirements"
          onClick={() => onChangeView("degree")}
        >
          {/* icon could go here */}
          <div className="home-tile-title">
            Degree – Course Requirements
          </div>
        </button>

        <button
          className="home-tile home-tile-prereqs"
          onClick={() => onChangeView("prereqs")}
        >
          {/* icon could go here */}
          <div className="home-tile-title">
            Degree – Course Ordering &amp; Prerequisites
          </div>
        </button>
      </section>
    </main>
  );
}

export default HomeView;