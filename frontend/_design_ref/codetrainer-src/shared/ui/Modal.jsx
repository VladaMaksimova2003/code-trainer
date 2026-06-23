// src/shared/ui/Modal.jsx
// Лёгкая модалка без зависимостей: backdrop, Esc, focus-trap, mobile-friendly ширина.
import { useEffect, useRef } from "react";

export default function Modal({ open, onClose, title, children, footer, labelledById = "modal-title" }) {
  const ref = useRef(null);
  const prevFocus = useRef(null);

  useEffect(() => {
    if (!open) return;
    prevFocus.current = document.activeElement;
    const node = ref.current;

    const onKey = (e) => {
      if (e.key === "Escape") {
        onClose?.();
        return;
      }
      if (e.key === "Tab" && node) {
        const focusables = node.querySelectorAll(
          'a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])'
        );
        if (!focusables.length) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          last.focus();
          e.preventDefault();
        } else if (!e.shiftKey && document.activeElement === last) {
          first.focus();
          e.preventDefault();
        }
      }
    };

    document.addEventListener("keydown", onKey);
    // focus first field
    const t = setTimeout(() => {
      const f = node?.querySelector(
        'textarea,input,button:not([disabled]),[tabindex]:not([tabindex="-1"])'
      );
      f?.focus();
    }, 30);

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKey);
      clearTimeout(t);
      document.body.style.overflow = prevOverflow;
      prevFocus.current?.focus?.();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[80] flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-6"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
    >
      <div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledById}
        className="w-full sm:w-[min(520px,calc(100vw-24px))] max-h-[92vh] flex flex-col
                   bg-surface border border-border rounded-t-xl sm:rounded-xl
                   shadow-[0_40px_90px_-30px_rgba(0,0,0,0.8)] animate-[modalpop_.16s_ease]"
      >
        {title && (
          <div className="flex items-center justify-between px-5 py-4 border-b border-border">
            <h2 id={labelledById} className="text-[15px] font-semibold text-ink">
              {title}
            </h2>
            <button
              type="button"
              aria-label="Закрыть"
              onClick={onClose}
              className="icon-btn h-8 w-8 text-ink-faint hover:text-ink"
            >
              ✕
            </button>
          </div>
        )}
        <div className="px-5 py-4 overflow-y-auto">{children}</div>
        {footer && (
          <div className="flex justify-end gap-2.5 px-5 py-4 border-t border-border">{footer}</div>
        )}
      </div>
    </div>
  );
}
