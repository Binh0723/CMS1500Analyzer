import { useState } from 'react'

import CMS1500Analyzer from './CMS1500Analyzer'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
    <CMS1500Analyzer />
  </div>
  )
}

export default App
