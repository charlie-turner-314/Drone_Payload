import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import Header from './Header'
import Logs from './Logs'
import Live from './Live'

import 'bootstrap/dist/css/bootstrap.min.css';

createRoot(document.getElementById('root')).render(
	<StrictMode>
		<BrowserRouter>
			<Header />
			<main>
				<Routes>
					<Route path='/logs' element={<Logs />} />
					<Route path='/' element={<Live />} />
				</Routes>
			</main>
		</BrowserRouter>
	</StrictMode>
)
