"""
SigeonOS Animation Engine
Reusable, buttery-smooth animation primitives for the entire OS.
Uses QPropertyAnimation, QGraphicsOpacityEffect, and custom easing.
Cleans up graphics effects after completion to prevent QPainter collisions and optimize performance.
"""
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QRect, QPoint, QSize, QTimer,
                          pyqtProperty, QObject, QAbstractAnimation)
from PyQt6.QtGui import QColor


# ──────────────────────────────────────────────
#  Fade In / Fade Out
# ──────────────────────────────────────────────

def fade_in(widget, duration=350, start=0.0, end=1.0, easing=QEasingCurve.Type.OutCubic, callback=None):
    """Smoothly fade a widget from transparent to opaque, then remove the effect for performance."""
    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(start)
    widget.show()

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(easing)
    
    def on_done():
        if end == 1.0:
            widget.setGraphicsEffect(None)
        if callback:
            callback()

    anim.finished.connect(on_done)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    # prevent GC
    widget._fade_anim = anim
    return anim


def fade_out(widget, duration=250, start=1.0, end=0.0, easing=QEasingCurve.Type.InCubic, callback=None):
    """Smoothly fade a widget from opaque to transparent."""
    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(start)

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(easing)
    
    def on_done():
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    anim.finished.connect(on_done)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._fade_anim = anim
    return anim


# ──────────────────────────────────────────────
#  Slide Animations
# ──────────────────────────────────────────────

def slide_in_from_bottom(widget, duration=300, offset=40, easing=QEasingCurve.Type.OutCubic, callback=None):
    """Slide widget up from below its current position + fade in."""
    target_pos = widget.pos()
    start_pos = QPoint(target_pos.x(), target_pos.y() + offset)
    widget.move(start_pos)
    widget.show()

    group = QParallelAnimationGroup(widget)

    # Position
    pos_anim = QPropertyAnimation(widget, b"pos", widget)
    pos_anim.setDuration(duration)
    pos_anim.setStartValue(start_pos)
    pos_anim.setEndValue(target_pos)
    pos_anim.setEasingCurve(easing)
    group.addAnimation(pos_anim)

    # Opacity
    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(0.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(duration)
    opa_anim.setStartValue(0.0)
    opa_anim.setEndValue(1.0)
    opa_anim.setEasingCurve(easing)
    group.addAnimation(opa_anim)

    def on_done():
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._slide_anim = group
    return group


def slide_out_to_bottom(widget, duration=200, offset=40, easing=QEasingCurve.Type.InCubic, callback=None):
    """Slide widget down below its current position + fade out, then hide."""
    start_pos = widget.pos()
    end_pos = QPoint(start_pos.x(), start_pos.y() + offset)

    group = QParallelAnimationGroup(widget)

    pos_anim = QPropertyAnimation(widget, b"pos", widget)
    pos_anim.setDuration(duration)
    pos_anim.setStartValue(start_pos)
    pos_anim.setEndValue(end_pos)
    pos_anim.setEasingCurve(easing)
    group.addAnimation(pos_anim)

    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(1.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(duration)
    opa_anim.setStartValue(1.0)
    opa_anim.setEndValue(0.0)
    opa_anim.setEasingCurve(easing)
    group.addAnimation(opa_anim)

    def _on_done():
        widget.hide()
        widget.move(start_pos)  # Reset position for next show
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(_on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._slide_anim = group
    return group


# ──────────────────────────────────────────────
#  Scale Pop-In (window open effect)
# ──────────────────────────────────────────────

def pop_in(widget, duration=300, easing=QEasingCurve.Type.OutBack, callback=None):
    """Scale + fade a widget from 85% to 100% size with a spring feel."""
    target_geo = widget.geometry()
    cx = target_geo.center().x()
    cy = target_geo.center().y()
    scale = 0.85
    sw = int(target_geo.width() * scale)
    sh = int(target_geo.height() * scale)
    start_geo = QRect(cx - sw // 2, cy - sh // 2, sw, sh)

    widget.setGeometry(start_geo)
    widget.show()

    group = QParallelAnimationGroup(widget)

    geo_anim = QPropertyAnimation(widget, b"geometry", widget)
    geo_anim.setDuration(duration)
    geo_anim.setStartValue(start_geo)
    geo_anim.setEndValue(target_geo)
    geo_anim.setEasingCurve(easing)
    group.addAnimation(geo_anim)

    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(0.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(int(duration * 0.6))
    opa_anim.setStartValue(0.0)
    opa_anim.setEndValue(1.0)
    opa_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    group.addAnimation(opa_anim)

    def on_done():
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._pop_anim = group
    return group


def pop_out(widget, duration=200, easing=QEasingCurve.Type.InBack, callback=None):
    """Scale + fade a widget from 100% down to 90% and vanish."""
    start_geo = widget.geometry()
    cx = start_geo.center().x()
    cy = start_geo.center().y()
    scale = 0.90
    ew = int(start_geo.width() * scale)
    eh = int(start_geo.height() * scale)
    end_geo = QRect(cx - ew // 2, cy - eh // 2, ew, eh)

    group = QParallelAnimationGroup(widget)

    geo_anim = QPropertyAnimation(widget, b"geometry", widget)
    geo_anim.setDuration(duration)
    geo_anim.setStartValue(start_geo)
    geo_anim.setEndValue(end_geo)
    geo_anim.setEasingCurve(easing)
    group.addAnimation(geo_anim)

    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(1.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(duration)
    opa_anim.setStartValue(1.0)
    opa_anim.setEndValue(0.0)
    opa_anim.setEasingCurve(QEasingCurve.Type.InQuad)
    group.addAnimation(opa_anim)

    def _on_done():
        widget.hide()
        widget.setGeometry(start_geo)
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(_on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._pop_anim = group
    return group


# ──────────────────────────────────────────────
#  Minimize to Taskbar (shrink toward bottom)
# ──────────────────────────────────────────────

def minimize_to_taskbar(widget, taskbar_y, duration=250, callback=None):
    """Shrink window down toward the taskbar position."""
    start_geo = widget.geometry()
    cx = start_geo.center().x()
    end_geo = QRect(cx - 20, taskbar_y - 10, 40, 10)

    group = QParallelAnimationGroup(widget)

    geo_anim = QPropertyAnimation(widget, b"geometry", widget)
    geo_anim.setDuration(duration)
    geo_anim.setStartValue(start_geo)
    geo_anim.setEndValue(end_geo)
    geo_anim.setEasingCurve(QEasingCurve.Type.InCubic)
    group.addAnimation(geo_anim)

    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(1.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(duration)
    opa_anim.setStartValue(1.0)
    opa_anim.setEndValue(0.0)
    opa_anim.setEasingCurve(QEasingCurve.Type.InQuad)
    group.addAnimation(opa_anim)

    def _on_done():
        widget.hide()
        widget.setGeometry(start_geo)
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(_on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._min_anim = group
    return group


# ──────────────────────────────────────────────
#  Restore from Taskbar (grow from bottom)
# ──────────────────────────────────────────────

def restore_from_taskbar(widget, target_geo, taskbar_y, duration=300, callback=None):
    """Grow window up from the taskbar position."""
    cx = target_geo.center().x()
    start_geo = QRect(cx - 20, taskbar_y - 10, 40, 10)
    widget.setGeometry(start_geo)
    widget.show()

    group = QParallelAnimationGroup(widget)

    geo_anim = QPropertyAnimation(widget, b"geometry", widget)
    geo_anim.setDuration(duration)
    geo_anim.setStartValue(start_geo)
    geo_anim.setEndValue(target_geo)
    geo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    group.addAnimation(geo_anim)

    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(0.0)
    opa_anim = QPropertyAnimation(effect, b"opacity", widget)
    opa_anim.setDuration(int(duration * 0.5))
    opa_anim.setStartValue(0.0)
    opa_anim.setEndValue(1.0)
    opa_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    group.addAnimation(opa_anim)

    def on_done():
        widget.setGraphicsEffect(None)
        if callback:
            callback()

    group.finished.connect(on_done)
    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._restore_anim = group
    return group


# ──────────────────────────────────────────────
#  Staggered Fade-In (for login screen elements)
# ──────────────────────────────────────────────

def staggered_fade_in(widgets, per_item_duration=350, delay_between=100, easing=QEasingCurve.Type.OutCubic):
    """Fade in a list of widgets one after another with a stagger delay."""
    for i, w in enumerate(widgets):
        effect = _ensure_opacity_effect(w)
        effect.setOpacity(0.0)
        QTimer.singleShot(i * delay_between, lambda ww=w, eff=effect: _do_stagger_fade(ww, eff, per_item_duration, easing))


def _do_stagger_fade(widget, effect, duration, easing):
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(easing)
    
    def on_done():
        widget.setGraphicsEffect(None)
        
    anim.finished.connect(on_done)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._stagger_anim = anim


# ──────────────────────────────────────────────
#  Pulsing Glow (for avatar on login)
# ──────────────────────────────────────────────

def pulse_glow(widget, duration=2000, min_opacity=0.5, max_opacity=1.0):
    """Continuously pulse a widget's opacity in a breathing pattern."""
    effect = _ensure_opacity_effect(widget)
    effect.setOpacity(max_opacity)

    group = QSequentialAnimationGroup(widget)
    a1 = QPropertyAnimation(effect, b"opacity", widget)
    a1.setDuration(duration // 2)
    a1.setStartValue(max_opacity)
    a1.setEndValue(min_opacity)
    a1.setEasingCurve(QEasingCurve.Type.InOutSine)

    a2 = QPropertyAnimation(effect, b"opacity", widget)
    a2.setDuration(duration // 2)
    a2.setStartValue(min_opacity)
    a2.setEndValue(max_opacity)
    a2.setEasingCurve(QEasingCurve.Type.InOutSine)

    group.addAnimation(a1)
    group.addAnimation(a2)
    group.setLoopCount(-1)
    group.start()
    widget._pulse_anim = group
    return group


def stop_pulse(widget):
    """Stop any running pulse animation and reset opacity."""
    if hasattr(widget, '_pulse_anim') and widget._pulse_anim:
        widget._pulse_anim.stop()
        widget._pulse_anim = None
    widget.setGraphicsEffect(None)


# ──────────────────────────────────────────────
#  Bounce (for hover on desktop icons)
# ──────────────────────────────────────────────

def bounce(widget, duration=400):
    """Quick bounce: move up 6px then spring back."""
    start = widget.pos()
    up = QPoint(start.x(), start.y() - 6)

    group = QSequentialAnimationGroup(widget)

    a1 = QPropertyAnimation(widget, b"pos", widget)
    a1.setDuration(duration // 2)
    a1.setStartValue(start)
    a1.setEndValue(up)
    a1.setEasingCurve(QEasingCurve.Type.OutQuad)
    group.addAnimation(a1)

    a2 = QPropertyAnimation(widget, b"pos", widget)
    a2.setDuration(duration // 2)
    a2.setStartValue(up)
    a2.setEndValue(start)
    a2.setEasingCurve(QEasingCurve.Type.OutBounce)
    group.addAnimation(a2)

    group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    widget._bounce_anim = group
    return group


# ──────────────────────────────────────────────
#  Drop Shadow helper
# ──────────────────────────────────────────────

def add_drop_shadow(widget, blur=20, offset_x=0, offset_y=4, color=QColor(0, 0, 0, 60)):
    """Attach a modern drop shadow to a widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(offset_x, offset_y)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)
    return shadow


# ──────────────────────────────────────────────
#  Internal Helper
# ──────────────────────────────────────────────

def _ensure_opacity_effect(widget):
    """Get or create a QGraphicsOpacityEffect on a widget."""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(1.0)
        widget.setGraphicsEffect(effect)
    return effect
