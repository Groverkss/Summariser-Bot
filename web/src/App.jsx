import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import "./App.css";

import firebase from "./firebase";

import Home from "./pages/Home";
import Record from "./pages/Record";
import NotFound from "./pages/NotFound";

// firebase.firestore().collection("bruh").add({
//     title: "idk",
//     duration: 20,
// });

const App = () => {
    return (
        <>
            <Router>
                <Switch>
                    <Route exact path="/" component={Home} />
                    <Route exact path="/records/:id" component={Record} />
                    <Route exact path="/404" component={NotFound} />
                    <Redirect to="/404" />
                </Switch>
            </Router>
        </>
    );
};

export default App;
