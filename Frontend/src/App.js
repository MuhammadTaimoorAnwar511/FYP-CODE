import React from 'react';
import { Route, Routes, useNavigate, } from 'react-router-dom';
import LoginPage from '../src/LoginSignup/loginPage';
import SignupPage from '../src/LoginSignup/signupPage';
import MarketOverview from '../src/MarketOverview/MarketOverview'; 
import Chart from '../src/Charts/Chart'
import LandingPage from '../src/LandingPage/LandingPage'
import Profile from '../src/Profile/Profile'
import Journal from '../src/Journal/Journal'
function App() {
  
  return (
    <Routes>
      <Route path='/' element = {<LandingPage/>}/>
      <Route path='/Login' element = {<LoginPage/>}/>
      <Route path='/register' element = {<SignupPage/>}/>
      <Route path='/MarketOverview' element = {<MarketOverview/>}/>
      <Route path='/Chart' element = {<Chart/>}/>
      <Route path='/Profile' element = {<Profile/>}/>
      <Route path='/Journal' element = {<Journal/>}/>
    </Routes>
  );
}

export default App;