<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  squareSize:       { type: Number,  default: 40 },
  borderColor:      { type: String,  default: '#1e293b' },
  hoverFillColor:   { type: String,  default: '#10b981' },
  hoverTrailAmount: { type: Number,  default: 4 },
  speed:            { type: Number,  default: 0.28 },
  direction:        { type: String,  default: 'diagonal' }, // up|down|left|right|diagonal
  shape:            { type: String,  default: 'square' },  // square|circle
  opacity:          { type: Number,  default: 1 },
})

const canvasRef = ref(null)

let animFrame = null
let cols = 0
let rows = 0
let tick = 0

// Each cell: { x, y, brightness, trail }
let cells = []

const hexToRgb = (hex) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return { r, g, b }
}

const lerp = (a, b, t) => a + (b - a) * t

const resize = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width  = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  cols = Math.ceil(canvas.width  / props.squareSize) + 2
  rows = Math.ceil(canvas.height / props.squareSize) + 2
  cells = []
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      cells.push({ col: c, row: r, brightness: 0 })
    }
  }
}

const getOffset = () => {
  const t = tick * props.speed
  switch (props.direction) {
    case 'up':       return { ox: 0, oy: -t % props.squareSize }
    case 'down':     return { ox: 0, oy:  t % props.squareSize }
    case 'left':     return { ox: -t % props.squareSize, oy: 0 }
    case 'right':    return { ox:  t % props.squareSize, oy: 0 }
    case 'diagonal': return { ox: t % props.squareSize, oy: t % props.squareSize }
    default:         return { ox: 0, oy: 0 }
  }
}

// Wave highlight using tick + cell index
const getWaveBrightness = (col, row) => {
  let phase
  switch (props.direction) {
    case 'diagonal': phase = (col + row) - tick * props.speed * 0.12; break
    case 'right':    phase = col          - tick * props.speed * 0.12; break
    case 'left':     phase = -col         - tick * props.speed * 0.12; break
    case 'down':     phase = row          - tick * props.speed * 0.12; break
    case 'up':       phase = -row         - tick * props.speed * 0.12; break
    default:         phase = 0
  }
  const sin = Math.sin(phase * 0.5)
  return Math.max(0, sin * 0.18) // subtle ambient wave
}

const hoverRgb = hexToRgb(props.hoverFillColor || '#10b981')

let mouse = { x: -9999, y: -9999 }

const onMouseMove = (e) => {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  mouse.x = e.clientX - rect.left
  mouse.y = e.clientY - rect.top
}

const onMouseLeave = () => { mouse = { x: -9999, y: -9999 } }

const draw = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const S = props.squareSize
  const { ox, oy } = getOffset()

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const borderRgb = hexToRgb(props.borderColor)

  for (let i = 0; i < cells.length; i++) {
    const cell = cells[i]
    const x = cell.col * S - (S - ox % S) + ox % S - S
    const y = cell.row * S - (S - oy % S) + oy % S - S

    // Real position with scroll offset
    const px = (cell.col * S + (ox % S)) - S
    const py = (cell.row * S + (oy % S)) - S

    // Hover influence
    const dx = mouse.x - (px + S / 2)
    const dy = mouse.y - (py + S / 2)
    const dist = Math.sqrt(dx * dx + dy * dy)
    const hoverRadius = S * (props.hoverTrailAmount + 1.5)
    const hoverStr = Math.max(0, 1 - dist / hoverRadius)

    // Wave ambient
    const wave = getWaveBrightness(cell.col, cell.row)

    // Combined brightness (target)
    const targetBrightness = Math.max(wave, hoverStr * 0.85)
    cell.brightness = lerp(cell.brightness, targetBrightness, 0.12)

    const b = cell.brightness

    // Fill color: interpolate from transparent to hoverFill
    const fillR = Math.round(lerp(0, hoverRgb.r, b))
    const fillG = Math.round(lerp(0, hoverRgb.g, b))
    const fillB = Math.round(lerp(0, hoverRgb.b, b))
    const fillA = b

    // Border color (constant)
    ctx.strokeStyle = `rgba(${borderRgb.r},${borderRgb.g},${borderRgb.b},0.5)`
    ctx.lineWidth = 0.5

    ctx.beginPath()
    if (props.shape === 'circle') {
      ctx.arc(px + S / 2, py + S / 2, S / 2 - 1, 0, Math.PI * 2)
    } else {
      ctx.rect(px + 0.5, py + 0.5, S - 1, S - 1)
    }

    if (fillA > 0.005) {
      ctx.fillStyle = `rgba(${fillR},${fillG},${fillB},${fillA})`
      ctx.fill()
    }
    ctx.stroke()
  }

  tick++
  animFrame = requestAnimationFrame(draw)
}

const ro = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(resize)
  : null

onMounted(() => {
  resize()
  const canvas = canvasRef.value
  canvas.addEventListener('mousemove', onMouseMove)
  canvas.addEventListener('mouseleave', onMouseLeave)
  if (ro) ro.observe(canvas)
  else window.addEventListener('resize', resize)
  draw()
})

onUnmounted(() => {
  cancelAnimationFrame(animFrame)
  const canvas = canvasRef.value
  if (canvas) {
    canvas.removeEventListener('mousemove', onMouseMove)
    canvas.removeEventListener('mouseleave', onMouseLeave)
  }
  if (ro) ro.disconnect()
  else window.removeEventListener('resize', resize)
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="absolute inset-0 w-full h-full pointer-events-auto"
    :style="{ opacity: props.opacity }"
  />
</template>
