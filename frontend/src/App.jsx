// src/App.jsx
import { useState } from "react";
import HomeView from "./views/HomeView.jsx";
import DegreeView from "./views/DegreeView.jsx";
import PrereqView from "./views/PrereqView.jsx";

function App() {
  // TODO: add state for display ("home" | "degree" | "prereqs") - Completed
  const [display, setDisplay] = useState("home");
  // TODO: add state for currentDegree (e.g., "it-sd" as a default) - Completed
  const [currentDegree, setCurrentDegree] = useState("example-degree");

  // TODO: handler to change the display based on a view name - Completed
  function handleChangeView(newDisplay) {
    setDisplay(newDisplay);
  }

  // TODO: handler to change the currentDegree when the selector changes - Completed
  function handleChangeDegree(newDegreeId) {
    setCurrentDegree(newDegreeId);
  }

  let content = null;

  // TODO: conditional rendering based on display - Completed
   if (display === "home") {
     content = <HomeView onChangeView={handleChangeView} />;
   } else if (display === "degree") {
     content = (
       <DegreeView
         currentDegree={currentDegree}
         onChangeView={handleChangeView}
         onChangeDegree={handleChangeDegree}
       />
     );
   } else if (display === "prereqs") {
     content = (
       <PrereqView
         currentDegree={currentDegree}
         onChangeView={handleChangeView}
         onChangeDegree={handleChangeDegree}
       />
     );
   }

  return (
    <div className="app-root">
      <header>
        <h1>My Academic Pathway (MAP) Planner</h1>
      </header>
      {content}
    </div>
  );
}

export default App;
