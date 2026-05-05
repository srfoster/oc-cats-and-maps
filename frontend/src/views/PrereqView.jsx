function PrereqView({ currentDegree, onChangeView, onChangeDegree }) {
  return (
    <main>
      <h2>Prereq View placeholder</h2>
      <p>Current degree id: {currentDegree}</p>
      <button onClick={() => onChangeView("home")}>
        Back to Home
      </button>
    </main>
  );
}

export default PrereqView;