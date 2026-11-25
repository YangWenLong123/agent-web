/*
 * @Author: along
 * @Description: 
 * @Date: 2026-10-26 11:56:24
 * @LastEditors: along
 * @LastEditTime: 2026-11-24 17:07:45
 * @FilePath: /my-react-app/src/App.jsx
 */
import { useState } from 'react'
import '@/assets/css/App.css'

function App() {
  const [count, setCount] = useState(0)
  const [step, setStep] = useState(1)

  const add = () => {
    setCount(count + step)
  }

  const decrement = () => {
    setCount(count - step)
  }

  const reset = () => {
    setCount(0)
  }

  return (
    <>
      <div>{count}</div>

      <div className="step-control">
        <label>
          步长：
          <input
            type="number"
            value={step}
            onChange={(e) => setStep(Number(e.target.value))}
            min="1"
          />
        </label>
      </div>
      
      <button type="button" className="counter" onClick={() => add()}>
        增加
      </button>
      <button type="button" className="counter" onClick={decrement}>
        减少
      </button>
      <button type="button" className="counter" onClick={reset}>
        重置
      </button>
    </>
  );
}

export default App
