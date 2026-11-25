// 读取完整或尚未闭合的 JSON 字符串；末尾未收齐的转义序列留待下一片段。
function readString(text, start) {
  let encoded = ''
  let cursor = start + 1
  while (cursor < text.length) {
    const character = text[cursor]
    if (character === '"') {
      return { value: JSON.parse(`"${encoded}"`), end: cursor, complete: true }
    }
    if (character === '\\') {
      const escape = text[cursor + 1]
      if (escape === 'u') {
        const hex = text.slice(cursor + 2, cursor + 6)
        if (!/^[\da-f]{4}$/i.test(hex)) break
        encoded += text.slice(cursor, cursor + 6)
        cursor += 6
        continue
      }
      if (!escape || !'"\\/bfnrt'.includes(escape)) break
      encoded += text.slice(cursor, cursor + 2)
      cursor += 2
      continue
    }
    if (character.charCodeAt(0) < 0x20) break
    encoded += character
    cursor += 1
  }
  const value = JSON.parse(`"${encoded}"`)
  // Unicode 代理对可能跨片段到达，先隐藏尚未配对的高代理字符。
  const last = value.charCodeAt(value.length - 1)
  return {
    value: last >= 0xd800 && last <= 0xdbff ? value.slice(0, -1) : value,
    end: cursor,
    complete: false,
  }
}

export function extractStreamingAnswer(text) {
  if (typeof text !== 'string' || !text.trimStart().startsWith('{')) return ''
  let depth = 0
  let expectsKey = false
  try {
    for (let cursor = 0; cursor < text.length; cursor += 1) {
      const character = text[cursor]
      if (character === '"') {
        const token = readString(text, cursor)
        if (!token.complete) return ''
        if (depth === 1 && expectsKey) {
          expectsKey = false
          if (token.value === 'answer') {
            const opening = /^\s*:\s*"/.exec(text.slice(token.end + 1))
            if (!opening) return ''
            return readString(text, token.end + opening[0].length).value
          }
        }
        cursor = token.end
      } else if (character === '{' || character === '[') {
        depth += 1
        if (depth === 1) expectsKey = true
      } else if (character === '}' || character === ']') {
        depth -= 1
      } else if (character === ',' && depth === 1) {
        expectsKey = true
      }
    }
  } catch {
    // 流尚未形成可读取字符串时保留空展示，最终格式校验仍由后端负责。
  }
  return ''
}
