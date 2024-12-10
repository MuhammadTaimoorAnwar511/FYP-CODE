import React from 'react';
import { Route, Routes, useNavigate, } from 'react-router-dom';
import LoginPage from '../src/LoginSignup/loginPage';
import SignupPage from '../src/LoginSignup/signupPage';
import MarketOverview from '../src/MarketOverview/MarketOverview'; 
import Chart from '../src/Charts/Chart'
import LandingPage from '../src/LandingPage/LandingPage'
function App() {
  
  return (
    <Routes>
      <Route path='/' element = {<LandingPage/>}/>
      <Route path='/Login' element = {<LoginPage/>}/>
      <Route path='/register' element = {<SignupPage/>}/>
      <Route path='/MarketOverview' element = {<MarketOverview/>}/>
      <Route path='/Chart' element = {<Chart/>}/>
      {/* <Route path='/' element = {<Login/>}/>
      <Route path='/registerSeller' element = {<Signup/>}/>
      <Route path='/mainpage' element = {<MainPage/>}/>
      <Route path='/myProfile' element = {<MyProfile/>}/>
      <Route path='/updateProfile' element = {<UpdateProfile/>}/>
      <Route path='/changePassword' element = {<ChangePassword/>}/>
      <Route path='/manageBalance' element = {<ManageBalance/>}/>
      <Route path='/deleteAccount' element = {<DeleteAccount/>}/>
      <Route path='/notifications' element = {<Notifications/>}/>
      <Route path='/seller/myProjects' element={<MyProjects/>}/>
      <Route path='/seller/project/:id' element={<DetailedProject/>}/>
      <Route path='/sellerSearch/project/:id' element={<SellerDetailedProject/>}/>
      <Route path='/chats/customer/:id' element={<CustById/>}/>
      <Route path='/chats' element={<AllCustomers/>}/>
      <Route path='/sellers' element={<SearchSellers/>}/>
      <Route path='/sellerSearch' element={<SearchedSellers/>}/>
      <Route path='/sellerSearch/:id' element={<SellerById/>}/> */}
    </Routes>
  );
}

export default App;