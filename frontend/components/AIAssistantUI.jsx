"use client"

import React, { useEffect, useMemo, useRef, useState } from "react"
import { Calendar, LayoutGrid, MoreHorizontal } from "lucide-react"
import Sidebar from "./Sidebar"
import Header from "./Header_Chatbot"
import ChatPane from "./ChatPane"
import GhostIconButton from "./GhostIconButton"
import ThemeToggle from "./ThemeToggle"
import { INITIAL_CONVERSATIONS, INITIAL_TEMPLATES, INITIAL_FOLDERS } from "./mockData"

export default function AIAssistantUI() {
  const [theme, setTheme] = useState(() => {
    const saved = typeof window !== "undefined" && localStorage.getItem("theme")
    if (saved) return saved
    if (typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
      return "dark"
    return "light"
  })

  useEffect(() => {
    try {
      if (theme === "dark") document.documentElement.classList.add("dark")
      else document.documentElement.classList.remove("dark")
      document.documentElement.setAttribute("data-theme", theme)
      document.documentElement.style.colorScheme = theme
      localStorage.setItem("theme", theme)
    } catch {}
  }, [theme])

  useEffect(() => {
    try {
      const media = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)")
      if (!media) return
      const listener = (e) => {
        const saved = localStorage.getItem("theme")
        if (!saved) setTheme(e.matches ? "dark" : "light")
      }
      media.addEventListener("change", listener)
      return () => media.removeEventListener("change", listener)
    } catch {}
  }, [])

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const raw = localStorage.getItem("sidebar-collapsed")
      return raw ? JSON.parse(raw) : { pinned: true, recent: false, folders: true, templates: true }
    } catch {
      return { pinned: true, recent: false, folders: true, templates: true }
    }
  })
  useEffect(() => {
    try {
      localStorage.setItem("sidebar-collapsed", JSON.stringify(collapsed))
    } catch {}
  }, [collapsed])

  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem("sidebar-collapsed-state")
      return saved ? JSON.parse(saved) : false
    } catch {
      return false
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem("sidebar-collapsed-state", JSON.stringify(sidebarCollapsed))
    } catch {}
  }, [sidebarCollapsed])

  const [conversations, setConversations] = useState(INITIAL_CONVERSATIONS)
  const [selectedId, setSelectedId] = useState(null)
  const [templates, setTemplates] = useState(INITIAL_TEMPLATES)
  const [folders, setFolders] = useState(INITIAL_FOLDERS)

  const [query, setQuery] = useState("")
  const searchRef = useRef(null)

  const [isThinking, setIsThinking] = useState(false)
  const [thinkingConvId, setThinkingConvId] = useState(null)

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "n") {
        e.preventDefault()
        createNewChat()
      }
      if (!e.metaKey && !e.ctrlKey && e.key === "/") {
        const tag = document.activeElement?.tagName?.toLowerCase()
        if (tag !== "input" && tag !== "textarea") {
          e.preventDefault()
          searchRef.current?.focus()
        }
      }
      if (e.key === "Escape" && sidebarOpen) setSidebarOpen(false)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [sidebarOpen, conversations])

  const initialized = useRef(false)

  useEffect(() => {
    if (!initialized.current && !selectedId) {
      initialized.current = true
      createNewChat()
    }
  }, [])

  const filtered = useMemo(() => {
    if (!query.trim()) return conversations
    const q = query.toLowerCase()
    return conversations.filter((c) => c.title.toLowerCase().includes(q) || c.preview.toLowerCase().includes(q))
  }, [conversations, query])

  const pinned = filtered.filter((c) => c.pinned).sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))

  const recent = filtered
    .filter((c) => !c.pinned)
    .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
    .slice(0, 10)

  const folderCounts = React.useMemo(() => {
    const map = Object.fromEntries(folders.map((f) => [f.name, 0]))
    for (const c of conversations) if (map[c.folder] != null) map[c.folder] += 1
    return map
  }, [conversations, folders])

  function togglePin(id) {
    setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, pinned: !c.pinned } : c)))
  }

  function deleteChat(id) {
    setConversations((prev) => prev.filter((c) => c.id !== id))
    if (selectedId === id) {
      setSelectedId(null)
    }
  }

  function createNewChat() {
    const id = Math.random().toString(36).slice(2)
    const item = {
      id,
      title: "New Chat",
      updatedAt: new Date().toISOString(),
      messageCount: 1,
      preview: "Please upload an image of your plant...",
      pinned: false,
      folder: "Work Projects",
      messages: [
        {
          id: Math.random().toString(36).slice(2),
          role: "assistant",
          content: "Hello! Please upload an image of your plant so I can help you diagnose any issues.",
          createdAt: new Date().toISOString(),
        }
      ],
    }
    setConversations((prev) => [item, ...prev])
    setSelectedId(id)
    setSidebarOpen(false)
  }

  function createFolder() {
    const name = prompt("Folder name")
    if (!name) return
    if (folders.some((f) => f.name.toLowerCase() === name.toLowerCase())) return alert("Folder already exists.")
    setFolders((prev) => [...prev, { id: Math.random().toString(36).slice(2), name }])
  }

  async function handleUpload(convId, file) {
    const now = new Date().toISOString()
    const imageUrl = URL.createObjectURL(file)

    const userMsg = {
      id: Math.random().toString(36).slice(2),
      role: "user",
      content: "Uploaded an image for analysis",
      image: imageUrl,
      createdAt: now
    }

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...(c.messages || []), userMsg]
        return {
          ...c,
          messages: msgs,
          updatedAt: now,
          messageCount: msgs.length,
          preview: "Uploaded an image...",
        }
      }),
    )

    setIsThinking(true)
    setThinkingConvId(convId)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const primaryUrl = process.env.NEXT_PUBLIC_API_URL || "/api/proxy"
      const fallbackUrl = "http://127.0.0.1:8000"

      let response
      try {
        response = await fetch(`${primaryUrl}/predict`, {
          method: "POST",
          body: formData,
        })
        if (!response.ok) throw new Error("Primary API failed")
      } catch (err) {
        console.warn("Primary API failed, trying fallback...", err)
        response = await fetch(`${fallbackUrl}/predict`, {
          method: "POST",
          body: formData,
        })
      }

      if (!response.ok) throw new Error("Prediction failed")

      const data = await response.json()

      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== convId) return c

          const asstMsg = {
            id: Math.random().toString(36).slice(2),
            role: "assistant",
            content: data.explanation,
            diagnosis: data.diagnosis,
            confidence: data.confidence,
            createdAt: new Date().toISOString(),
          }

          const msgs = [...(c.messages || []), asstMsg]
          return {
            ...c,
            title: data.diagnosis.split('___').join(' '),
            messages: msgs,
            updatedAt: new Date().toISOString(),
            messageCount: msgs.length,
            preview: asstMsg.content.slice(0, 80),
            context: data.chat_context,
            diagnosis: data.diagnosis
          }
        }),
      )
    } catch (error) {
      console.error(error)
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== convId) return c
          const errorMsg = {
            id: Math.random().toString(36).slice(2),
            role: "assistant",
            content: "Sorry, I encountered an error analyzing the image. Please try again.",
            createdAt: new Date().toISOString(),
          }
          return {
            ...c,
            messages: [...(c.messages || []), errorMsg],
            updatedAt: new Date().toISOString(),
            messageCount: (c.messages || []).length + 1,
          }
        }),
      )
    } finally {
      setIsThinking(false)
      setThinkingConvId(null)
    }
  }

  function sendMessage(convId, content) {
    if (!content.trim()) return
    const now = new Date().toISOString()
    const userMsg = { id: Math.random().toString(36).slice(2), role: "user", content, createdAt: now }

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...(c.messages || []), userMsg]
        return {
          ...c,
          messages: msgs,
          updatedAt: now,
          messageCount: msgs.length,
          preview: content.slice(0, 80),
        }
      }),
    )

    setIsThinking(true)
    setThinkingConvId(convId)

    const currentConvId = convId

    // Check if we have context for this conversation
    const conversation = conversations.find(c => c.id === convId)

    if (conversation?.context) {
      // Chat mode
      const primaryUrl = process.env.NEXT_PUBLIC_API_URL || "/api/proxy"
      const fallbackUrl = "http://127.0.0.1:8000"

      const fetchOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: content,
          context: conversation.context,
          diagnosis: conversation.diagnosis
        })
      }

      fetch(`${primaryUrl}/chat`, fetchOptions)
      .catch(() => fetch(`${fallbackUrl}/chat`, fetchOptions))
      .then(res => res.json())
      .then(data => {
        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== currentConvId) return c
            const asstMsg = {
              id: Math.random().toString(36).slice(2),
              role: "assistant",
              content: data.answer || "Sorry, I encountered an error.",
              createdAt: new Date().toISOString(),
            }
            const msgs = [...(c.messages || []), asstMsg]
            return {
              ...c,
              messages: msgs,
              updatedAt: new Date().toISOString(),
              messageCount: msgs.length,
              preview: (asstMsg.content || "").slice(0, 80),
            }
          }),
        )
      })
      .catch(err => {
        console.error(err)
        // Handle error
      })
      .finally(() => {
        setIsThinking(false)
        setThinkingConvId(null)
      })
    } else {
      // Fallback for no context (or handle as before)
      setTimeout(() => {
        setIsThinking(false)
        setThinkingConvId(null)
        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== currentConvId) return c
            const ack = `Please upload an image first so I can help you.`
            const asstMsg = {
              id: Math.random().toString(36).slice(2),
              role: "assistant",
              content: ack,
              createdAt: new Date().toISOString(),
            }
            const msgs = [...(c.messages || []), asstMsg]
            return {
              ...c,
              messages: msgs,
              updatedAt: new Date().toISOString(),
              messageCount: msgs.length,
              preview: asstMsg.content.slice(0, 80),
            }
          }),
        )
      }, 1000)
    }
  }

  function editMessage(convId, messageId, newContent) {
    const now = new Date().toISOString()
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = (c.messages || []).map((m) =>
          m.id === messageId ? { ...m, content: newContent, editedAt: now } : m,
        )
        return {
          ...c,
          messages: msgs,
          preview: msgs[msgs.length - 1]?.content?.slice(0, 80) || c.preview,
        }
      }),
    )
  }

  function resendMessage(convId, messageId) {
    const conv = conversations.find((c) => c.id === convId)
    const msg = conv?.messages?.find((m) => m.id === messageId)
    if (!msg) return
    sendMessage(convId, msg.content)
  }

  function pauseThinking() {
    setIsThinking(false)
    setThinkingConvId(null)
  }

  function handleUseTemplate(template) {
    // This will be passed down to the Composer component
    // The Composer will handle inserting the template content
    if (composerRef.current) {
      composerRef.current.insertTemplate(template.content)
    }
  }

  const composerRef = useRef(null)

  const selected = conversations.find((c) => c.id === selectedId) || null

  return (
    <div className="h-screen w-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <div className="md:hidden sticky top-0 z-40 flex items-center gap-2 border-b border-zinc-200/60 bg-white/80 px-3 py-2 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/70">
        <div className="ml-1 flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="inline-flex h-4 w-4 items-center justify-center">✱</span> Fluora Bot
        </div>
        <div className="ml-auto flex items-center gap-2">
          <GhostIconButton label="Schedule">
            <Calendar className="h-4 w-4" />
          </GhostIconButton>
          <GhostIconButton label="Apps">
            <LayoutGrid className="h-4 w-4" />
          </GhostIconButton>
          <GhostIconButton label="More">
            <MoreHorizontal className="h-4 w-4" />
          </GhostIconButton>
          <ThemeToggle theme={theme} setTheme={setTheme} />
        </div>
      </div>

      <div className="flex h-[calc(100vh-0px)] w-full">
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          theme={theme}
          setTheme={setTheme}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarCollapsed={setSidebarCollapsed}
          conversations={conversations}
          pinned={pinned}
          recent={recent}
          folders={folders}
          folderCounts={folderCounts}
          selectedId={selectedId}
          onSelect={(id) => setSelectedId(id)}
          togglePin={togglePin}
          deleteChat={deleteChat}
          query={query}
          setQuery={setQuery}
          searchRef={searchRef}
          createFolder={createFolder}
          createNewChat={createNewChat}
          templates={templates}
          setTemplates={setTemplates}
          onUseTemplate={handleUseTemplate}
        />

        <main className="relative flex min-w-0 flex-1 flex-col">
          <Header createNewChat={createNewChat} sidebarCollapsed={sidebarCollapsed} setSidebarOpen={setSidebarOpen} />
          <ChatPane
            ref={composerRef}
            conversation={selected}
            onSend={(content) => selected && sendMessage(selected.id, content)}
            onUpload={(file) => selected && handleUpload(selected.id, file)}
            onEditMessage={(messageId, newContent) => selected && editMessage(selected.id, messageId, newContent)}
            onResendMessage={(messageId) => selected && resendMessage(selected.id, messageId)}
            isThinking={isThinking && thinkingConvId === selected?.id}
            onPauseThinking={pauseThinking}
          />
        </main>
      </div>
    </div>
  )
}
